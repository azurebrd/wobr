#!/usr/bin/perl 

# test stuff about amigo

# test inferred dag view  2013 07 16

# ebi has a better graph in "Term Hierarchy"
# http://www.ebi.ac.uk/ontology-lookup/browse.do?ontName=GO&termId=GO%3A0033554&termName=cellular%20response%20to%20stress
# http://www.ebi.ac.uk/ontology-lookup/browse.do?ontName=GO&termId=GO:0034051&termName=cellular%20response%20to%20stress
#
# wormbase display 
# https://www.wormbase.org/species/all/go_term/GO:0033554#2--10
#
# berkeleybop display 
# http://amigo2.berkeleybop.org/cgi-bin/amigo2/amigo/term/GO:0033554
#
# berkeleybop json
# http://golr.berkeleybop.org/select?qt=standard&fl=*&version=2.2&wt=json&indent=on&rows=1&q=id:%22GO:0033554%22&fq=document_category:%22ontology_class%22
#
# graphviz documentation
# http://search.cpan.org/~rsavage/GraphViz-2.14/lib/GraphViz.pm
#
# using GraphViz to generate an SVG with clickable links to other nodes in the graph.
# using JSON to parse the json from berkeleybop
# using LWP::Simple to get json from berkeleybop
# given a goid, generate an svg graph with clickable nodes and make a separate table of children if there's too many.  for Raymond.  2013 07 17
#
# make an inferred tree view using  regulates_transitivity_graph_json  edges from the json.
# Raymond suggests that the depth of indentation corresponds to the longest path from main node to root.
# couldn't find a longest path method in Graph.pm .  2013 07 18
#
# changed directory and repo to "wobr" (worm ontology browser) for Raymond.  2013 07 22


use CGI;
use strict;
use LWP::Simple;
use JSON;
use GraphViz;


# my $gviz = GraphViz->new(width=>10, height=>8);
my $gviz = GraphViz->new();
my $json = JSON->new->allow_nonref;
my $query = new CGI;

my %paths;					# finalpath => array of nodes for longest path ; graph -> parent node -> child node

&process();

sub process {
  my $action;                   # what user clicked
  unless ($action = $query->param('action')) { $action = 'none'; }

  if ($action eq 'Tree') { &dag(); }
    else { &dag(); }				# no action, show dag by default
} # sub process

sub getTopoHash {
  my ($goid) = @_;
  my $url = "http://golr.berkeleybop.org/select?qt=standard&fl=*&version=2.2&wt=json&indent=on&rows=1&q=id:%22" . $goid . "%22&fq=document_category:%22ontology_class%22";
  
  my $page_data = get $url;
  
  my $perl_scalar = $json->decode( $page_data );
  my %jsonHash = %$perl_scalar;

  my $topo_data = $json->decode( $jsonHash{"response"}{"docs"}[0]{"topology_graph_json"} );
  my $trans_data = $json->decode( $jsonHash{"response"}{"docs"}[0]{"regulates_transitivity_graph_json"} );
  return ($topo_data, $trans_data);
} # sub getTopoHash


sub dag {
  &printHtmlHeader(); 
  my ($var, $val) = &getHtmlVar($query, 'goid');

  my $goid = "GO:0033554";		# default goid if none given
  if ($val) { $goid = $val; }

  my ($topo_data, $trans_data) = &getTopoHash($goid);
  my %topo = %$topo_data;
  my %trans = %$trans_data;

  my %transitivity;
  for my $index (0 .. @{ $trans{"edges"} }) {
    my ($sub, $obj, $pred) = ('', '', '');
    if ($trans{"edges"}[$index]{'sub'}) {  $sub  = $trans{"edges"}[$index]{'sub'};  }
    if ($trans{"edges"}[$index]{'obj'}) {  $obj  = $trans{"edges"}[$index]{'obj'};  }
    if ($trans{"edges"}[$index]{'pred'}) { $pred = $trans{"edges"}[$index]{'pred'}; }
    $transitivity{$obj} = $pred;
  }
  
  my %children; 			# children of the wanted goid, value is relationship type (predicate) ; are the corresponding nodes on an edge where the object is the goid
  my %ancestors;			# ancestors are nodes that are neither the GOID nor its children
  my %child;				# for any term, each subkey is a child
  my (@edges) = @{ $topo{"edges"} };
  for my $index (0 .. @edges) {
    my ($sub, $obj, $pred) = ('', '', '');
    if ($edges[$index]{'sub'}) { $sub = $edges[$index]{'sub'}; }
    if ($edges[$index]{'obj'}) { $obj = $edges[$index]{'obj'}; }
    if ($edges[$index]{'pred'}) { $pred = $edges[$index]{'pred'}; }
    if ($obj eq $goid) { $children{$sub} = $pred; }		# track children here
  }

  my %colorMap;
  $colorMap{"is_a"}                 = 'black';
  $colorMap{"part_of"}              = 'blue';
  $colorMap{"has_part"}             = 'purple';
  $colorMap{"regulates"}            = 'orange';
  $colorMap{"positively_regulates"} = 'green';
  $colorMap{"negatively_regulates"} = 'red';
  $colorMap{"occurs_in"}            = 'cyan';
  
  my (@edges) = @{ $topo{"edges"} };
  for my $index (0 .. @edges) {
    my ($sub, $obj, $pred) = ('', '', '');
    if ($edges[$index]{'sub'}) { $sub = $edges[$index]{'sub'}; }
    if ($edges[$index]{'obj'}) { $obj = $edges[$index]{'obj'}; }
    if ($edges[$index]{'pred'}) { $pred = $edges[$index]{'pred'}; }
    my $color = 'black'; if ($colorMap{$pred}) { $color = $colorMap{$pred}; }
    if ($sub && $obj && $pred) { 
      if ($children{$sub}) { next; }	# don't add edge for the children
      $paths{"graph"}{"$obj"}{"$sub"}++;	# put all child nodes under parent node
      $child{$sub}{$obj}++;
      $gviz->add_edge("$obj" => "$sub", dir => "back", label => "$pred", color => "$color", fontcolor => "$color");
    } # if ($sub && $obj && $pred)
  } # for my $index (0 .. @edges)

  my %label;				# id to name
  my (@nodes) = @{ $topo{"nodes"} };
  for my $index (0 .. @nodes) {
    my ($id, $lbl) = ('', '');
    if ($nodes[$index]{'id'}) { $id = $nodes[$index]{'id'}; }
    if ($nodes[$index]{'lbl'}) { $lbl = $nodes[$index]{'lbl'}; }
    $label{$id} = $lbl;
    if ($children{$id}) { next; }	# don't add node for the children
    unless ($id eq $goid) { $ancestors{$id}++; }		# ancestors are nodes that are neither the GOID nor its children
    my $url = "amigo.cgi?action=Tree&goid=$id";
    $lbl =~ s/ /\\n/g;
    if ($id && $lbl) { $gviz->add_node("$id", label => "$id\n$lbl", shape => "box", color => "red", URL => "$url"); }	# have GOID and name in the node
  }

  print qq(<embed width="200" height="100" type="image/svg+xml" src="whatsource.svg">\n);
  my $svgGenerated = $gviz->as_svg;
  my ($svgMarkup) = $svgGenerated =~ m/(<svg.*<\/svg>)/s;
  print qq($svgMarkup\n);
  print qq(</embed>\n);

  my $child_table = ''; my $ancestor_table = '';
    $child_table .= "children : <br/>\n";
    $child_table .= qq(<table border="1"><tr><th>relationship</th><th>id</th><th>name</th></tr>\n);
    foreach my $child (sort keys %children) {
      my $relationship = $children{$child};
      my ($link_child) = &makeLink($child, $child);
      my $child_name = $label{$child};
      my ($link_childname) = &makeLink($child, $child_name);
      $child_table .= qq(<tr><td>$relationship</td><td>$link_child</td><td>$link_childname</td></tr>\n);
    } # foreach my $goid (sort keys %children)
    $child_table .= qq(</table>\n);
# to display childer table, uncomment
#   if ($child_table) { print $child_table; }

  my %inferredTree;		# sort nodes by depth of steps (longest path)
  my $max_indent = 0;		# how many steps is the longest path, will indent that much
  $ancestor_table .= "ancestors : <br/>\n";
  $ancestor_table .= qq(<table border="1"><tr><th>steps</th><th>relationship</th><th>id</th><th>name</th></tr>\n);
  foreach my $ancestor (sort keys %ancestors) {
    next unless $ancestor;
    my $relationship = $transitivity{$ancestor};
    my ($link_ancestor) = &makeLink($ancestor, $ancestor);
    my $ancestor_name = $label{$ancestor};
    my ($link_ancestorname) = &makeLink($ancestor, $ancestor_name);
    my ($max_steps) = &getLongestPath( $ancestor, $goid );		# most steps between ancestor and goid
    my $indentation = $max_steps - 1; if ($indentation > $max_indent) { $max_indent = $indentation; }
    $inferredTree{$indentation}{qq($relationship : $link_ancestor $link_ancestorname)}++;
    $ancestor_table .= qq(<tr><td>$max_steps</td><td>$relationship</td><td>$link_ancestor</td><td>$link_ancestorname</td></tr>\n);
  } # foreach my $goid (sort keys %ancestors)
  $ancestor_table .= qq(</table>\n);
# to display ancestor table, uncomment
#   print $ancestor_table;

  print "<br/><br/><br/>\n";
  my $spacer = '&nbsp;&nbsp;&nbsp;';
  foreach my $depth (reverse sort {$a<=>$b} keys %inferredTree) {
    foreach my $row (sort keys %{ $inferredTree{$depth} }) {
      my $indentation = $max_indent - $depth;			# indentation is max indent minux depth
      for (1 .. $indentation) { print $spacer; }		# for each indentation print the corresponding spacer
      print qq($row<br/>\n); } }				# print the data row
  for (1 .. $max_indent) { print $spacer; }			# add indentation for main term
  print qq($spacer<span style="color:green">$goid : $label{$goid}</span><br/>\n);	# add data for main term
  foreach my $child (sort keys %children) {			# for each child
    my $relationship = $children{$child};
    my ($link_child) = &makeLink($child, $child);		# make link to id
    my $child_name = $label{$child};
    my ($link_childname) = &makeLink($child, $child_name);	# make link to name
    for (1 .. $max_indent) { print $spacer; }			# add indentation for children term
    print $spacer . $spacer . qq($relationship : $link_child $link_childname<br/>\n);	# add data for child
  } # foreach my $goid (sort keys %children)
  
  &printHtmlFooter(); 
} # sub dag

sub getLongestPath {
  my ($ancestor, $goid) = @_;						# the ancestor and goid from which to find the longest path
  &recurseLongestPath($ancestor, $ancestor, $goid, $ancestor);		# recurse to find longest path given current, start, end, and list of current path
  my $max_nodes = 0;							# the most nodes found among all paths travelled
  foreach my $finpath (@{ $paths{"finalpath"} }) {			# for each of the paths that reached the end node
    my $nodes = scalar @$finpath;					# amount of nodes in the path
    if ($nodes > $max_nodes) { $max_nodes = $nodes; }			# if more nodes than max, set new max
  } # foreach my $finpath (@finalpath)
  delete $paths{"finalpath"};						# reset finalpath for other ancestors
  my $max_steps = $max_nodes - 1;					# amount of steps is one less than amount of nodes
  return $max_steps;
} # sub getLongestPath 

sub recurseLongestPath {
  my ($current, $start, $end, $curpath) = @_;				# current node, starting node, end node, path travelled so far
  foreach my $child (sort keys %{ $paths{"graph"}{$current} }) {	# for each child of the current node
    my @curpath = split/\t/, $curpath;					# convert current path to array
    push @curpath, $child;						# add the current child
    if ($child eq $end) {						# if current child is the end node
        my @tmpWay = @curpath;						# make a copy of the array
        push @{ $paths{"finalpath"} }, \@tmpWay; }			# put a reference to the array copy into the finalpath
      else {								# not the end node yet
        my $curpath = join"\t", @curpath;				# pass literal current path instead of reference
        &recurseLongestPath($child, $start, $end, $curpath); }		# recurse to keep looking for the final node
  } # foreach $child (sort keys %{ $paths{"graph"}{$current} })
} # sub recurseLongestPath

sub makeLink {
  my ($goid, $text) = @_;
  my $url = "amigo.cgi?action=Tree&goid=$goid";
  my $link = qq(<a href="$url">$text</a>);
  return $link;
} # sub makeLink

sub printHtmlFooter { print qq(</body></html>\n); }

sub printHtmlHeader { print qq(Content-type: text/html\n\n<html><head><title>Amigo testing</title></head><body>\n); }

sub getHtmlVar {                
  no strict 'refs';             
  my ($query, $var, $err) = @_; 
  unless ($query->param("$var")) {
    if ($err) { print "<FONT COLOR=blue>ERROR : No such variable : $var</FONT><BR>\n"; }
  } else { 
    my $oop = $query->param("$var");
    $$var = &untaint($oop);         
    return ($var, $$var);           
  } 
} # sub getHtmlVar

sub untaint {
  my $tainted = shift;
  my $untainted;
  if ($tainted eq "") {
    $untainted = "";
  } else { # if ($tainted eq "")
    $tainted =~ s/[^\w\-.,;:?\/\\@#\$\%\^&*\>\<(){}[\]+=!~|' \t\n\r\f\"€‚ƒ„…†‡ˆ‰Š‹ŒŽ‘’“”•—˜™š›œžŸ¡¢£¤¥¦§¨©ª«¬­®¯°±²³´µ¶·¹º»¼½¾¿ÀÁÂÃÄÅÆÇÈÉÊËÌÍÎÏÐÑÒÓÔÕÖ×ØÙÚÛÜÝÞßàáâãäåæçèéêëìíîïðñòóôõö÷øùúûüýþ]//g;
    if ($tainted =~ m/^([\w\-.,;:?\/\\@#\$\%&\^*\>\<(){}[\]+=!~|' \t\n\r\f\"€‚ƒ„…†‡ˆ‰Š‹ŒŽ‘’“”•—˜™š›œžŸ¡¢£¤¥¦§¨©ª«¬­®¯°±²³´µ¶·¹º»¼½¾¿ÀÁÂÃÄÅÆÇÈÉÊËÌÍÎÏÐÑÒÓÔÕÖ×ØÙÚÛÜÝÞßàáâãäåæçèéêëìíîïðñòóôõö÷øùúûüýþ]+)$/) {
      $untainted = $1;
    } else {
      die "Bad data Tainted in $tainted";
    }
  } # else # if ($tainted eq "")
  return $untainted;
} # sub untaint



__END__

        "regulates_transitivity_graph_json":"{\"nodes\":[{\"id\":\"GO:0019222\",\"lbl\":\"regulation of metabolic process\"},{\"id\":\"GO:0043487\",\"lbl\":\"regulation of RNA stability\"},{\"id\":\"GO:0044763\",\"lbl\":\"single-organism cellular process\"},{\"id\":\"GO:0043488\",\"lbl\":\"regulation of mRNA stability\"},{\"id\":\"GO:0009987\",\"lbl\":\"cellular process\"},{\"id\":\"GO:0044699\",\"lbl\":\"single-organism process\"},{\"id\":\"GO:0065007\",\"lbl\":\"biological regulation\"},{\"id\":\"GO:0006950\",\"lbl\":\"response to stress\"},{\"id\":\"GO:0065008\",\"lbl\":\"regulation of biological quality\"},{\"id\":\"GO:0008152\",\"lbl\":\"metabolic process\"},{\"id\":\"GO:0033554\",\"lbl\":\"cellular response to stress\"},{\"id\":\"GO:0060255\",\"lbl\":\"regulation of macromolecule metabolic process\"},{\"id\":\"GO:0008150\",\"lbl\":\"biological_process\"},{\"id\":\"GO:0050896\",\"lbl\":\"response to stimulus\"},{\"id\":\"GO:0010608\",\"lbl\":\"posttranscriptional regulation of gene expression\"},{\"id\":\"GO:0051716\",\"lbl\":\"cellular response to stimulus\"},{\"id\":\"GO:0010610\",\"lbl\":\"regulation of mRNA stability involved in response to stress\"},{\"id\":\"GO:0050789\",\"lbl\":\"regulation of biological process\"},{\"id\":\"GO:0010467\",\"lbl\":\"gene expression\"},{\"id\":\"GO:0010468\",\"lbl\":\"regulation of gene expression\"},{\"id\":\"GO:0043170\",\"lbl\":\"macromolecule metabolic process\"},{\"id\":\"GO:0071704\",\"lbl\":\"organic substance metabolic process\"}],\"edges\":[{\"sub\":\"GO:0010610\",\"obj\":\"GO:0006950\",\"pred\":\"part_of\"},{\"sub\":\"GO:0010610\",\"obj\":\"GO:0044699\",\"pred\":\"part_of\"},{\"sub\":\"GO:0010610\",\"obj\":\"GO:0065007\",\"pred\":\"is_a\"},{\"sub\":\"GO:0010610\",\"obj\":\"GO:0009987\",\"pred\":\"part_of\"},{\"sub\":\"GO:0010610\",\"obj\":\"GO:0043170\",\"pred\":\"is_a\"},{\"sub\":\"GO:0010610\",\"obj\":\"GO:0010467\",\"pred\":\"is_a\"},{\"sub\":\"GO:0010610\",\"obj\":\"GO:0019222\",\"pred\":\"is_a\"},{\"sub\":\"GO:0010610\",\"obj\":\"GO:0008150\",\"pred\":\"is_a\"},{\"sub\":\"GO:0010610\",\"obj\":\"GO:0043170\",\"pred\":\"regulates\"},{\"sub\":\"GO:0010610\",\"obj\":\"GO:0008150\",\"pred\":\"regulates\"},{\"sub\":\"GO:0010610\",\"obj\":\"GO:0010608\",\"pred\":\"is_a\"},{\"sub\":\"GO:0010610\",\"obj\":\"GO:0006950\",\"pred\":\"is_a\"},{\"sub\":\"GO:0010610\",\"obj\":\"GO:0008152\",\"pred\":\"is_a\"},{\"sub\":\"GO:0010610\",\"obj\":\"GO:0008152\",\"pred\":\"regulates\"},{\"sub\":\"GO:0010610\",\"obj\":\"GO:0033554\",\"pred\":\"part_of\"},{\"sub\":\"GO:0010610\",\"obj\":\"GO:0008150\",\"pred\":\"part_of\"},{\"sub\":\"GO:0010610\",\"obj\":\"GO:0010467\",\"pred\":\"regulates\"},{\"sub\":\"GO:0010610\",\"obj\":\"GO:0050896\",\"pred\":\"part_of\"},{\"sub\":\"GO:0010610\",\"obj\":\"GO:0060255\",\"pred\":\"is_a\"},{\"sub\":\"GO:0010610\",\"obj\":\"GO:0071704\",\"pred\":\"regulates\"},{\"sub\":\"GO:0010610\",\"obj\":\"GO:0010468\",\"pred\":\"is_a\"},{\"sub\":\"GO:0010610\",\"obj\":\"GO:0050789\",\"pred\":\"is_a\"},{\"sub\":\"GO:0010610\",\"obj\":\"GO:0043487\",\"pred\":\"is_a\"},{\"sub\":\"GO:0010610\",\"obj\":\"GO:0065008\",\"pred\":\"is_a\"},{\"sub\":\"GO:0010610\",\"obj\":\"GO:0033554\",\"pred\":\"is_a\"},{\"sub\":\"GO:0010610\",\"obj\":\"GO:0043488\",\"pred\":\"is_a\"},{\"sub\":\"GO:0010610\",\"obj\":\"GO:0044763\",\"pred\":\"part_of\"},{\"sub\":\"GO:0010610\",\"obj\":\"GO:0051716\",\"pred\":\"part_of\"}]}",

 "topology_graph_json":"{\"nodes\":[{\"id\":\"GO:0019222\",\"lbl\":\"regulation of metabolic process\"},{\"id\":\"GO:0043487\",\"lbl\":\"regulation of RNA stability\"},{\"id\":\"GO:0044763\",\"lbl\":\"single-organism cellular process\"},{\"id\":\"GO:0009987\",\"lbl\":\"cellular process\"},{\"id\":\"GO:0043488\",\"lbl\":\"regulation of mRNA stability\"},{\"id\":\"GO:0044699\",\"lbl\":\"single-organism process\"},{\"id\":\"GO:0006950\",\"lbl\":\"response to stress\"},{\"id\":\"GO:0065007\",\"lbl\":\"biological regulation\"},{\"id\":\"GO:0065008\",\"lbl\":\"regulation of biological quality\"},{\"id\":\"GO:2000815\",\"lbl\":\"regulation of mRNA stability involved in response to oxidative stress\"},{\"id\":\"GO:0008152\",\"lbl\":\"metabolic process\"},{\"id\":\"GO:0060255\",\"lbl\":\"regulation of macromolecule metabolic process\"},{\"id\":\"GO:0008150\",\"lbl\":\"biological_process\"},{\"id\":\"GO:0033554\",\"lbl\":\"cellular response to stress\"},{\"id\":\"GO:0050896\",\"lbl\":\"response to stimulus\"},{\"id\":\"GO:0010608\",\"lbl\":\"posttranscriptional regulation of gene expression\"},{\"id\":\"GO:0010610\",\"lbl\":\"regulation of mRNA stability involved in response to stress\"},{\"id\":\"GO:0051716\",\"lbl\":\"cellular response to stimulus\"},{\"id\":\"GO:0050789\",\"lbl\":\"regulation of biological process\"},{\"id\":\"GO:0010467\",\"lbl\":\"gene expression\"},{\"id\":\"GO:0010468\",\"lbl\":\"regulation of gene expression\"},{\"id\":\"GO:0043170\",\"lbl\":\"macromolecule metabolic process\"},{\"id\":\"GO:0071704\",\"lbl\":\"organic substance metabolic process\"}],\"edges\":[{\"sub\":\"GO:0006950\",\"obj\":\"GO:0050896\",\"pred\":\"is_a\"},{\"sub\":\"GO:0051716\",\"obj\":\"GO:0050896\",\"pred\":\"is_a\"},{\"sub\":\"GO:0010610\",\"obj\":\"GO:0006950\",\"pred\":\"part_of\"},{\"sub\":\"GO:0019222\",\"obj\":\"GO:0008152\",\"pred\":\"regulates\"},{\"sub\":\"GO:0033554\",\"obj\":\"GO:0006950\",\"pred\":\"is_a\"},{\"sub\":\"GO:0019222\",\"obj\":\"GO:0050789\",\"pred\":\"is_a\"},{\"sub\":\"GO:0010468\",\"obj\":\"GO:0060255\",\"pred\":\"is_a\"},{\"sub\":\"GO:0043170\",\"obj\":\"GO:0071704\",\"pred\":\"is_a\"},{\"sub\":\"GO:0050789\",\"obj\":\"GO:0065007\",\"pred\":\"is_a\"},{\"sub\":\"GO:0043487\",\"obj\":\"GO:0010608\",\"pred\":\"is_a\"},{\"sub\":\"GO:0050896\",\"obj\":\"GO:0008150\",\"pred\":\"is_a\"},{\"sub\":\"GO:0050789\",\"obj\":\"GO:0008150\",\"pred\":\"regulates\"},{\"sub\":\"GO:0044763\",\"obj\":\"GO:0044699\",\"pred\":\"is_a\"},{\"sub\":\"GO:0010610\",\"obj\":\"GO:0033554\",\"pred\":\"part_of\"},{\"sub\":\"GO:0008152\",\"obj\":\"GO:0008150\",\"pred\":\"is_a\"},{\"sub\":\"GO:0071704\",\"obj\":\"GO:0008152\",\"pred\":\"is_a\"},{\"sub\":\"GO:0010468\",\"obj\":\"GO:0010467\",\"pred\":\"regulates\"},{\"sub\":\"GO:0043487\",\"obj\":\"GO:0065008\",\"pred\":\"is_a\"},{\"sub\":\"GO:0065007\",\"obj\":\"GO:0008150\",\"pred\":\"is_a\"},{\"sub\":\"GO:0010468\",\"obj\":\"GO:0065007\",\"pred\":\"is_a\"},{\"sub\":\"GO:0065008\",\"obj\":\"GO:0065007\",\"pred\":\"is_a\"},{\"sub\":\"GO:0010608\",\"obj\":\"GO:0010468\",\"pred\":\"is_a\"},{\"sub\":\"GO:0060255\",\"obj\":\"GO:0019222\",\"pred\":\"is_a\"},{\"sub\":\"GO:0010467\",\"obj\":\"GO:0043170\",\"pred\":\"is_a\"},{\"sub\":\"GO:0044699\",\"obj\":\"GO:0008150\",\"pred\":\"is_a\"},{\"sub\":\"GO:0060255\",\"obj\":\"GO:0065007\",\"pred\":\"is_a\"},{\"sub\":\"GO:0019222\",\"obj\":\"GO:0065007\",\"pred\":\"is_a\"},{\"sub\":\"GO:0033554\",\"obj\":\"GO:0051716\",\"pred\":\"is_a\"},{\"sub\":\"GO:0044763\",\"obj\":\"GO:0009987\",\"pred\":\"is_a\"},{\"sub\":\"GO:0043488\",\"obj\":\"GO:0043487\",\"pred\":\"is_a\"},{\"sub\":\"GO:0009987\",\"obj\":\"GO:0008150\",\"pred\":\"is_a\"},{\"sub\":\"GO:0051716\",\"obj\":\"GO:0044763\",\"pred\":\"is_a\"},{\"sub\":\"GO:0010610\",\"obj\":\"GO:0043488\",\"pred\":\"is_a\"},{\"sub\":\"GO:2000815\",\"obj\":\"GO:0010610\",\"pred\":\"is_a\"},{\"sub\":\"GO:0060255\",\"obj\":\"GO:0043170\",\"pred\":\"regulates\"}]}",
