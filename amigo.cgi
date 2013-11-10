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
# do not trust regulates_transitivity_graph_json edges in term 80135, 9987 is_a doesn't make sense.  regulates_transitivity_graph_json has just the ancestors.
# topology_graph_json has ancestors and children, and edges have relationship between direct nodes.
#
# berkeleybop json for direct genes
# http://golr.berkeleybop.org/select?qt=standard&indent=on&wt=json&version=2.2&fl=*%2Cscore&fq=&q=*:*&fq=document_category:%22bioentity%22&fq=source:%22WB%22&fq=annotation_class_list:%22GO:0006950%22	# with fl wildcard that returns a lot of data
# http://golr.berkeleybop.org/select?qt=standard&indent=on&wt=json&version=2.2&fl=id%2Cscore&fq=&q=*:*&fq=document_category:%22bioentity%22&fq=source:%22WB%22&fq=annotation_class_list:%22GO:0006950%22
# http://golr.berkeleybop.org/select?qt=standard&indent=on&wt=json&version=2.2&fl=id&start=0&rows=10000000&fq=&q=*:*&fq=document_category:%22bioentity%22&fq=source:%22WB%22&fq=annotation_class_list:%22GO:0006950%22	# with wbgenes listed
# http://golr.berkeleybop.org/select?qt=standard&indent=on&wt=json&version=2.2&fl=id&start=0&rows=10000000&q=document_category:bioentity&fq=source:%22WB%22&fq=%7B!cache=false%7Dannotation_class_list:%22GO:0006950%22	# with wbgenes listed, more specific q, cache off
#
# berkeleybop json for genes by inference (direct + indirect)
# http://golr.berkeleybop.org/select?qt=standard&indent=on&wt=json&version=2.2&fl=*%2Cscore&fq=&q=*:*&fq=document_category:%22bioentity%22&fq=source:%22WB%22&fq=regulates_closure:%22GO:0006950%22	# with fl wildcard that returns a lot of data
# http://golr.berkeleybop.org/select?qt=standard&indent=on&wt=json&version=2.2&fl=%2Cscore&fq=&q=*:*&fq=document_category:%22bioentity%22&fq=source:%22WB%22&fq=regulates_closure:%22GO:0006950%22
# http://golr.berkeleybop.org/select?qt=standard&indent=on&wt=json&version=2.2&fl=id&start=0&rows=10000000&fq=&q=*:*&fq=document_category:%22bioentity%22&fq=source:%22WB%22&fq=regulates_closure:%22GO:0006950%22	# with wbgenes listed
# http://golr.berkeleybop.org/select?qt=standard&indent=on&wt=json&version=2.2&fl=id&start=0&rows=10000000&q=document_category:bioentity&fq=source:%22WB%22&fq=%7B!cache=false%7Dregulates_closure:%22GO:0006950%22	# with wbgenes listed, more specific q, cache off
#
# expandable ul display
# http://sequenceontology.org/browser/current_svn/term/SO:0000625  
#
# graphviz documentation
# http://search.cpan.org/~rsavage/GraphViz-2.14/lib/GraphViz.pm
#
# solr reference guide
# https://cwiki.apache.org/confluence/display/solr/Apache+Solr+Reference+Guide
#
# using GraphViz to generate an SVG with clickable links to other nodes in the graph.
# using JSON to parse the json from berkeleybop
# using LWP::Simple to get json from berkeleybop
# given a goid, generate an svg graph with clickable nodes and make a separate table of children if there's too many.  for Raymond.  2013 07 17
#
# make an inferred tree view using  regulates_transitivity_graph_json  edges from the json. # this is later found to be wrong on 2013 07 25
# Raymond suggests that the depth of indentation corresponds to the longest path from main node to root.
# couldn't find a longest path method in Graph.pm .  2013 07 18
#
# changed directory and repo to "wobr" (worm ontology browser) for Raymond.  2013 07 22
#
# add number of direct genes and inferred genes to each item in inferred tree view.  link those to another page that lists each gene.  
# pre-loading all the genes to display was taking too long because of getting all lists of genes for all go terms from berkeleybop.  2013 07 23
#
# concentrate image, change fontsize, remove label from edges, add a legend for edges.  
# given each of the main term's parents, list siblings from that parent in an expandable table.  2013 07 24
#
# added graphViz legend as separate image (I don't like it)
# regulates_transitivity_graph_json  from json does not give proper dominant inferred transitivity, deriving it from each final path using
#   inferred transitivity of pairs  http://www.geneontology.org/GO.ontology-ext.relations.shtml 
#   and dominant transitivity of multiple path from  ChewableGraph.pm	2013 07 26
#
# Raymond found single URLs for JSON to get gene counts for direct/inferred for a given goid and all its children, and using a single URL for direct and a single for inferred is waaaay faster ; these URLs may not give correct children counts though.  Raymond and Chris feel we don't need the count for ancestors.
# direct url
# 'http://golr.berkeleybop.org/select?qt=standard&indent=on&wt=json&version=2.2&fl=id&start=0&rows=10000000&q=document_category:bioentity&facet=true&facet.field=annotation_class_list&facet.limit=-1&facet.mincount=1&facet.prefix=GO&facet.sort=count&fq=source:%22WB%22&fq=annotation_class_list:%22' . $goid . '%22';
# inferred url
# 'http://golr.berkeleybop.org/select?qt=standard&indent=on&wt=json&version=2.2&fl=id&start=0&rows=10000000&q=document_category:bioentity&facet=true&facet.field=regulates_closure&facet.limit=-1&facet.mincount=1&facet.prefix=GO&facet.sort=count&fq=source:%22WB%22&fq=regulates_closure:%22' . $goid . '%22'; 
# Combined  &showInferredGenes();  and  &showDirectGenes();  into the single  &showGenes();  2013 07 30
#
# do not display direct gene products in inferred tree view.  for Raymond.
# when showing page with list of genes for a goterm, always show both direct and inferred with direct on top (for Ranjana)
# tried to clean up working of sibblings link, but raymond and chris can't decide on what it should show or how.  2013 08 01
#
# Changed url for solr queries to Raymond's virtual machine.  2013 08 06
#
# Changed display so siblings table to have an extra column for indentation, and for the links to expand and contract change the
# innerHTML of the span to a plus or minus, accordingly.  2013 08 07
#
# Added  &treeExpand();  and  &queryChildren();  to get an expandable tree display of GO terms, working off of solr only, no postgres.  2013 09 02
#
# Generalized this and javascript to work for any ontology term, working off of termIDs instead of termNumbers.
# Added root terms for expandable tree for worm anatomy, disease ontology, worm development, elegans phenotype ontology.  2013 10 28
#
# %ancestors for %inferredTree now comes from transitivity json instead of topology.
# Added more %colorMap values for new types.  2013 10 31
#
# changed $solr_url to be a $base_solr_url and created &getSolrUrl to generate the $solr_url based on the identifier prefix
# to direct to the proper solr subdirectory.  2013 11 09


use CGI;
use strict;
use LWP::Simple;
use JSON;
use GraphViz;

# use DBI;		# for postgres, get rid of this later
# my $dbh = DBI->connect ( "dbi:Pg:dbname=wobrdb", "", "") or die "Cannot connect to database!\n";
# my $result;


# my $gviz = GraphViz->new(width=>10, height=>8);
# my $gviz = GraphViz->new();
my $gviz = GraphViz->new(concentrate => 'concentrate');
my $gviz_legend = GraphViz->new(concentrate => 'concentrate', rankdir  => 'BT');
my $json = JSON->new->allow_nonref;
my $query = new CGI;
my $base_solr_url = 'http://131.215.12.220:8080/solr/';		# raymond URL 2013 08 06
# my $solr_url = 'http://golr.berkeleybop.org/';

my %paths;	# finalpath => array of all (array of nodes of paths that end)
		# childToParent -> child node -> parent node => relationship
		# # parentToChild -> parent node -> child node => relationship

&process();

sub process {
  my $action;                   # what user clicked
  unless ($action = $query->param('action')) { $action = 'none'; }

  if ($action eq 'Tree') { &dag(); }
    elsif ($action eq 'showGenes')         { &showGenes(); }
    elsif ($action eq 'queryChildren') { &queryChildren(); }

#     elsif ($action eq 'showInferredGenes') { &showInferredGenes(); }	# combined into the single &showGenes();
#     elsif ($action eq 'showDirectGenes') {   &showDirectGenes();   }	# combined into the single &showGenes();
    else { &dag(); }				# no action, show dag by default
} # sub process

sub getSolrUrl {
  my ($focusTermId) = @_;
  my ($identifierType) = $focusTermId =~ m/^(\w+):/;
  my %idToSubdirectory;
  $idToSubdirectory{"WBbt"}        = "anatomy";
  $idToSubdirectory{"DOID"}        = "disease";
  $idToSubdirectory{"GO"}          = "go";
  $idToSubdirectory{"WBls"}        = "lifestage";
  $idToSubdirectory{"WBPhenotype"} = "phenotype";
  my $solr_url = $base_solr_url . $idToSubdirectory{$identifierType} . '/';
} # sub getSolrUrl

sub getTopoHash {
  my ($focusTermId) = @_;
  my ($solr_url) = &getSolrUrl($focusTermId);
  my $url = $solr_url . "select?qt=standard&fl=*&version=2.2&wt=json&indent=on&rows=1&q=id:%22" . $focusTermId . "%22&fq=document_category:%22ontology_class%22";
  
  my $page_data = get $url;
  
  my $perl_scalar = $json->decode( $page_data );
  my %jsonHash = %$perl_scalar;

  my $topoHashref = $json->decode( $jsonHash{"response"}{"docs"}[0]{"topology_graph_json"} );
#   return ($topoHashref);
  my $transHashref = $json->decode( $jsonHash{"response"}{"docs"}[0]{"regulates_transitivity_graph_json"} );	# need this for inferred Tree View
  return ($topoHashref, $transHashref);
} # sub getTopoHash

sub getTopoChildrenParents {
  my ($focusTermId, $topoHref) = @_;
  my %topo = %$topoHref;
  my %children; 			# children of the wanted focusTermId, value is relationship type (predicate) ; are the corresponding nodes on an edge where the object is the focusTermId
  my %parents;				# direct parents of the wanted focusTermId, value is relationship type (predicate) ; are the corresponding nodes on an edge where the subject is the focusTermId
  my %child;				# for any term, each subkey is a child
  my (@edges) = @{ $topo{"edges"} };
  for my $index (0 .. @edges) {
    my ($sub, $obj, $pred) = ('', '', '');
    if ($edges[$index]{'sub'}) { $sub = $edges[$index]{'sub'}; }
    if ($edges[$index]{'obj'}) { $obj = $edges[$index]{'obj'}; }
    if ($edges[$index]{'pred'}) { $pred = $edges[$index]{'pred'}; }
    if ($obj eq $focusTermId) { $children{$sub} = $pred; }		# track children here
    if ($sub eq $focusTermId) { $parents{$obj}  = $pred; }		# track parents here
  }
  return (\%children, \%parents);
} # sub getTopoChildrenParents

sub queryChildren {                             # generate the html for the unordered list of a go number, produce list items and unordered lists to expand each child of the go number
  print qq(Content-type: text/plain\n\n\n);
#   my ($var, $goNumber) = &getHtmlVar($query, 'goNumber');
#   my $goid = 'GO:' . $goNumber;                 # get the goid from the go number
  my ($var, $termId) = &getHtmlVar($query, 'termId');
  my %hash;                                     # for a child :  relationship is the termId's relationship to the original termId ; name is the termId's name ; hasChildren is the count of children if the child is itself a parent of other termId

# solr way of getting data
  my ($topoHashref, $transHashref) = &getTopoHash($termId);
  my %topo = %$topoHashref;
  my ($childrenHashref, $parentsHashref) = &getTopoChildrenParents($termId, $topoHashref);
  my %children = %$childrenHashref;
  my (@nodes) = @{ $topo{"nodes"} };		# use nodes to add sibling termId labels to %label
  for my $index (0 .. @nodes) {
    my ($id, $lbl) = ('', '');
    if ($nodes[$index]{'id'}) { $id = $nodes[$index]{'id'}; }
    if ($nodes[$index]{'lbl'}) { $lbl = $nodes[$index]{'lbl'}; }
    next unless ($children{$id});		# only get names of ids that are children of main term
#     $label{$id} = $lbl;
    $hash{$id}{name} = $lbl; }
  foreach my $child (sort keys %children) {	# for each child get their name from %children and whether they have children from solr
    $hash{$child}{relationship} = $children{$child};
    my ($topoChildHashref, $transChildHashref) = &getTopoHash($child);
    my %topoChild = %$topoChildHashref;
    my ($childChildrenHashref, $childParentsHashref) = &getTopoChildrenParents($child, $topoChildHashref);
    my %grandchildren = %$childChildrenHashref;
    if (scalar keys %grandchildren > 0) { $hash{$child}{hasChildren}++; }
  } # foreach my $child (sort keys %children)

# psql way of getting data
#   $result = $dbh->prepare( "SELECT goid_child, relationship FROM obo_goid_edges WHERE goid_parent = '$goid'" );         # get the goid's children and relationship
#   $result->execute() or die "Cannot prepare statement: $DBI::errstr\n";
#   while (my @row = $result->fetchrow) {
#     my ($child, $relationship) = @row;
#     $hash{$child}{relationship} = $relationship;
#   }
#   my $goids = join"','", keys %hash;            # get the goids of all children
#   $result = $dbh->prepare( "SELECT * FROM obo_goid_name WHERE goid_goid IN ('$goids')" );       # get the names of the children
#   $result->execute() or die "Cannot prepare statement: $DBI::errstr\n";
#   while (my @row = $result->fetchrow) {
#     $hash{$row[0]}{name} = $row[1]; }
#   $result = $dbh->prepare( "SELECT goid_parent FROM obo_goid_edges WHERE goid_parent IN ('$goids')" );  # get the count of children for each child
#   $result->execute() or die "Cannot prepare statement: $DBI::errstr\n";
#   while (my @row = $result->fetchrow) {
#     my ($parent) = @row;
#     $hash{$parent}{hasChildren}++;
#   }

  foreach my $child (sort keys %hash) {         # for each child
    my $expand_link = '&nbsp;';                 # no expand link is a literal space
#     my ($goNumber) = $child =~ m/GO:(\d+)/;     # get the child's go number
    if ($hash{$child}{hasChildren}) {           # if the child has children, create a link to expand and get its children
#       $expand_link = qq(<span style="text-decoration: underline; color: blue; cursor: pointer;" id="toggle_$goNumber" onclick="expandGoid('$goNumber');" >+</span>);
      $expand_link = qq(<span style="text-decoration: underline; color: blue; cursor: pointer;" id="toggle_$child" onclick="expandTermId('$child');" >+</span>); }
    print qq(<li>$expand_link );                                        # print a list item with the link to expand if there should be one
    print qq($hash{$child}{relationship} );                             # print the relationship
    print qq($child $hash{$child}{name});                               # print the child's go name
#     print qq(<ul id="children_$goNumber" style="display: none">);	# make another unordered list to store the child's children and hide it by default
#     print qq(<li><input id="notQueried_$goNumber" value="loading"></li></ul></li>);	# add a list item to the list and an input element to state that this termId has not been queried before
    print qq(<ul id="children_$child" style="display: none">);		# make another unordered list to store the child's children and hide it by default
    print qq(<li><input id="notQueried_$child" value="loading"></li></ul></li>);	# add a list item to the list and an input element to state that this termId has not been queried before
  } # foreach my $child (sort keys %hash)
} # sub queryChildren

sub treeExpand {
  my ($var, $rootTerm) = &getHtmlVar($query, 'focusTermId');
  my @rootTerms = qw( GO:0008150 GO:0005575 GO:0003674 WBbt:0000100 DOID:4 WBls:0000075 WBPhenotype:0000886 );	# by default have the 7 main roots
  if ($rootTerm) {
#     ($rootTerm) = $rootTerm =~ m/(\d+)/;                        # just the digits
    @rootTerms = ( $rootTerm ); }                               # if given a go number, use that instead

  my %names; my %hasChildren;
# psql way to get data
#   my $goids = join"','GO:", @rootTerms;                 # get the names of all the root terms
#   $result = $dbh->prepare( "SELECT * FROM obo_goid_name WHERE goid_goid IN ('GO:$goids')" );    # get the names of the children
#   $result->execute() or die "Cannot prepare statement: $DBI::errstr\n";
#   while (my @row = $result->fetchrow) { $names{$row[0]} = $row[1]; }

# solr way to get data
  foreach my $termId (@rootTerms) {
#     my $goid = 'GO:' . $gonum;
#     my ($topoHashref) = &getTopoHash($termId);
    my ($topoHashref, $transHashref) = &getTopoHash($termId);
    my %topo  = %$topoHashref;
    my %trans = %$transHashref;
    my ($childrenHashref, $parentsHashref) = &getTopoChildrenParents($termId, $topoHashref);
    my %children = %$childrenHashref;
    if (scalar keys %children > 0) { $hasChildren{$termId}++; }
    my (@nodes) = @{ $topo{"nodes"} };		# use nodes to add sibling termId labels to %label
    for my $index (0 .. @nodes) {
      my ($id, $lbl) = ('', '');
      if ($nodes[$index]{'id'}) { $id = $nodes[$index]{'id'}; }
      if ($nodes[$index]{'lbl'}) { $lbl = $nodes[$index]{'lbl'}; }
      $names{$id} = $lbl; }
  } # foreach my $termId (@rootTerms)

  print qq(<form method="post" action="amigo.cgi">);
  print qq(A different ID to be the focus term : <input name="focusTermId"> e.g. GO:0033554 WBbt:0000100 DOID:4 WBls:0000075 WBPhenotype:0000886<br/></form>);
  foreach my $rootTerm ( @rootTerms ) {
#      my $expand_link = qq(<span style="text-decoration: underline; color: blue; cursor: pointer;" id="toggle_$rootTerm" onclick="expandGoid('$rootTerm');" >+</span>);  # span link to expand node by doing a jquery off of the cgi
     my $expand_link = qq(<span style="text-decoration: underline; color: blue; cursor: pointer;" id="toggle_$rootTerm" onclick="expandTermId('$rootTerm');" >+</span>);  # span link to expand node by doing a jquery off of the cgi
     unless ($hasChildren{$rootTerm}) { $expand_link = ''; }
     print qq(<ul><li id="$rootTerm">$expand_link $rootTerm $names{"$rootTerm"});	# start an unordered list with only element the rootTerm
     print qq(<ul id="children_$rootTerm" style="display: none">);                      # add within another unordered list for the children of this rootTerm, hide by default because clicking to query and load its values will toggle its show/hide state
     print qq(<li><input id="notQueried_$rootTerm" value="loading"></li></ul>);		# add a list item to the list and an input element to state that this rootTerm has not been queried before
     print qq(</li></ul>);                                                              # close the root unordered list and list item
  }
} # sub treeExpand

sub dag {
  &printHtmlHeader(); 

#   my ($var, $val) = &getHtmlVar($query, 'goid');
  my ($var, $val) = &getHtmlVar($query, 'focusTermId');

  my $focusTermId = "GO:0033554";		# default focusTermId if none given
  if ($val) { $focusTermId = $val; }

  my ($topoHashref, $transHashref) = &getTopoHash($focusTermId);
  my %topo = %$topoHashref;
  my %trans = %$transHashref;

#   This is bad, transitivity is not correct in the  regulates_transitivity_graph_json  from berkeleybop
#   my ($topoHashref, $transHashref) = &getTopoHash($goid);
#   my %trans = %$transHashref;
#   my %transitivity;
#   for my $index (0 .. @{ $trans{"edges"} }) {
#     my ($sub, $obj, $pred) = ('', '', '');
#     if ($trans{"edges"}[$index]{'sub'}) {  $sub  = $trans{"edges"}[$index]{'sub'};  }
#     if ($trans{"edges"}[$index]{'obj'}) {  $obj  = $trans{"edges"}[$index]{'obj'};  }
#     if ($trans{"edges"}[$index]{'pred'}) { $pred = $trans{"edges"}[$index]{'pred'}; }
#     $transitivity{$obj} = $pred;
#   }

#   my %children; 			# children of the wanted goid, value is relationship type (predicate) ; are the corresponding nodes on an edge where the object is the goid
#   my %parents;				# direct parents of the wanted goid, value is relationship type (predicte) ; are the corresponding nodes on an edge where the subject is the goid
#   my (@edges) = @{ $topo{"edges"} };
#   for my $index (0 .. @edges) {
#     my ($sub, $obj, $pred) = ('', '', '');
#     if ($edges[$index]{'sub'}) { $sub = $edges[$index]{'sub'}; }
#     if ($edges[$index]{'obj'}) { $obj = $edges[$index]{'obj'}; }
#     if ($edges[$index]{'pred'}) { $pred = $edges[$index]{'pred'}; }
#     if ($obj eq $goid) { $children{$sub} = $pred; }		# track children here
#     if ($sub eq $goid) { $parents{$obj}  = $pred; }		# track parents here
#   }

  my ($childrenHashref, $parentsHashref) = &getTopoChildrenParents($focusTermId, $topoHashref);
  my %children = %$childrenHashref;
  my %parents  = %$parentsHashref;

  my %colorMap;
  $colorMap{"is_a"}                          = 'black';
  $colorMap{"part_of"}                       = 'blue';
  $colorMap{"has_part"}                      = 'purple';
  $colorMap{"regulates"}                     = 'orange';
  $colorMap{"positively_regulates"}          = 'green';
  $colorMap{"negatively_regulates"}          = 'red';
  $colorMap{"occurs_in"}                     = 'cyan';
  $colorMap{"daughter of"}                   = 'pink';
  $colorMap{"daughter of in hermaphrodite"}  = 'pink';
  $colorMap{"daughter of in male"}           = 'pink';
  $colorMap{"develops from"}                 = 'brown';
  $colorMap{"xunion_of"}                     = 'brown';
  $colorMap{"exclusive union of"}            = 'brown';
  my %edgeTypeExists;
  
  my %child;				# for any term, each subkey is a child
  my (@edges) = @{ $topo{"edges"} };
  for my $index (0 .. @edges) {
    my ($sub, $obj, $pred) = ('', '', '');
    if ($edges[$index]{'sub'}) {  $sub  = $edges[$index]{'sub'};  }
    if ($edges[$index]{'obj'}) {  $obj  = $edges[$index]{'obj'};  }
    if ($edges[$index]{'pred'}) { $pred = $edges[$index]{'pred'}; }
    if ($sub && $obj && $pred) { 
      if ($children{$sub}) { next; }	# don't add edge for the children
      my $color = 'black'; if ($colorMap{$pred}) { $color = $colorMap{$pred}; $edgeTypeExists{$pred}++; }
#       $paths{"parentToChild"}{"$obj"}{"$sub"} = $pred;	# put all child nodes under parent node	# NOT USED 
      $paths{"childToParent"}{"$sub"}{"$obj"} = $pred;	# put all parent nodes under child node
      $child{$sub}{$obj}++;
#       $gviz->add_edge("$obj" => "$sub", dir => "back", label => "$pred", color => "$color", fontcolor => "$color");
      $gviz->add_edge("$obj" => "$sub", dir => "back", color => "$color", fontcolor => "$color");
#       print qq("$obj" => "$sub", dir => "back", PRED $pred : color => "$color", fontcolor => "$color"<br>\n);
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
#     unless ($id eq $focusTermId) { $ancestors{$id}++; }		# ancestors are nodes that are neither the GOID nor its children ; should come from transitivity not topology 2013 10 31
    my $url = "amigo.cgi?action=Tree&focusTermId=$id";
    $lbl =~ s/ /\\n/g;
    if ($id && $lbl) { $gviz->add_node("$id", label => "$id\n$lbl", shape => "box", fontsize => "10", color => "red", URL => "$url"); }	# have GOID and name in the node
  }

  foreach my $pred (sort keys %edgeTypeExists) {
    my $color = $colorMap{$pred};
    $gviz_legend->add_node("A_$pred", label => "A", shape => "box", fontsize => "10", color => "red");
    $gviz_legend->add_node("B_$pred", label => "B", shape => "box", fontsize => "10", color => "red");
    $gviz_legend->add_edge("A_$pred" => "B_$pred", label => "$pred", color => "$color", fontsize => "10", fontcolor => "black");
    print qq(<span style="color:$color">------> </span>$pred<br/>\n);	# make a legend using html, it's not in the same style as graphViz
  }

#   print qq(<embed width="200" height="100" type="image/svg+xml" src="whatsource.svg">\n);	# if generating an image and embedding it
  my $svgGenerated = $gviz->as_svg;
  my ($svgMarkup) = $svgGenerated =~ m/(<svg.*<\/svg>)/s;
  print qq($svgMarkup\n);
#   print qq(</embed>\n);

    # make a legend using graphViz, it's kind of bulky
  my $svgLegendGenerated = $gviz_legend->as_svg;
  my ($svgLegendMarkup) = $svgLegendGenerated =~ m/(<svg.*<\/svg>)/s;
  print qq($svgLegendMarkup\n);

  my $parent_table = '';
  if (scalar keys %parents > 0) { 
    $parent_table .= qq(<br/><br/><br/><br/>);
    $parent_table .= qq(parents of <span style="color:green">$focusTermId : $label{$focusTermId}</span> : \n);
    foreach my $parent (sort keys %parents) {
      my $relationship = $parents{$parent};
      my $name = $label{$parent};
      my ($link_parent) = &makeLink($parent, $parent);
      my ($link_name) = &makeLink($parent, $name);
#       my $siblingsLink = qq(<br/><span style="text-decoration: underline; color: blue; cursor: pointer;" onclick="toggleShowHide('table_siblings_$parent');">display siblings</span>);
#       $parent_table .= qq($siblingsLink through parent $link_parent $relationship $link_name);
      my $siblingsLink = qq(<span id="span_plusMinus_$parent" style="border:solid 1px black; cursor: pointer;" onclick="togglePlusMinus('span_plusMinus_$parent'); toggleShowHide('table_siblings_$parent');">&nbsp;+&nbsp;</span>);
      $parent_table .= qq(<br/>$link_parent $siblingsLink);
#       my ($topoHashref) = &getTopoHash($parent);
      my ($topoHashref, $transHashref) = &getTopoHash($parent);
      my %topo  = %$topoHashref;
      my %trans = %$transHashref;

      my (@nodes) = @{ $topo{"nodes"} };		# use nodes to add sibling focusTermId labels to %label
      for my $index (0 .. @nodes) {
        my ($id, $lbl) = ('', '');
        if ($nodes[$index]{'id'}) { $id = $nodes[$index]{'id'}; }
        if ($nodes[$index]{'lbl'}) { $lbl = $nodes[$index]{'lbl'}; }
        $label{$id} = $lbl; }

      my ($siblingsHashref, $grandparentsHashref) = &getTopoChildrenParents($parent, $topoHashref);
      my %siblings = %$siblingsHashref;
      my @siblingRows = ();
      foreach my $sibling (sort keys %siblings) {
        next if ($sibling eq $focusTermId);
        my $sib_rel = $siblings{$sibling};
        my $name = $label{$sibling};
        my ($link_sibling) = &makeLink($sibling, $sibling);
        my ($link_name) = &makeLink($sibling, $name);
#         $parent_table .= qq( $sib_rel $link_sibling $link_name <br/> );
        push @siblingRows, qq(<tr><td width="30"></td><td>$sib_rel</td><td>$link_sibling</td><td>$link_name</tr>);
      }
      if (scalar @siblingRows > 0) {
        $parent_table .= qq(<table id="table_siblings_$parent" style="display: none">);
        foreach my $siblingRow (@siblingRows) { $parent_table .= $siblingRow; }
        $parent_table .= qq(</table>); }
    } # foreach my $parent (sort keys %parents)
  }
  if ($parent_table) { print $parent_table; }
  

  my $child_table = ''; my $ancestor_table = '';
    $child_table .= "children : <br/>\n";
    $child_table .= qq(<table border="1"><tr><th>relationship</th><th>id</th><th>name</th></tr>\n);
    foreach my $child (sort keys %children) {
      my $relationship = $children{$child};
      my ($link_child) = &makeLink($child, $child);
      my $child_name = $label{$child};
      my ($link_childname) = &makeLink($child, $child_name);
      $child_table .= qq(<tr><td>$relationship</td><td>$link_child</td><td>$link_childname</td></tr>\n);
    } # foreach my $child (sort keys %children)
    $child_table .= qq(</table>\n);
# to display childer table, uncomment
#   if ($child_table) { print $child_table; }

  my %ancestors;			# ancestors are nodes that are neither the GOID nor its children
  my (@tnodes) = @{ $trans{"nodes"} };	# for inferred tree view, use transitivity instead of topology
  for my $index (0 .. @tnodes) {
    my ($id, $lbl) = ('', '');
    if ($tnodes[$index]{'id'}) { $id = $tnodes[$index]{'id'}; }
#     if ($children{$id}) { next; }	# don't add node for the children
    unless ($id eq $focusTermId) { $ancestors{$id}++; }		# ancestors are nodes that are neither the GOID nor its children
  } 

  my %inferredTree;		# sort nodes by depth of steps (longest path)
  my $max_indent = 0;		# how many steps is the longest path, will indent that much
  $ancestor_table .= "ancestors : <br/>\n";
  $ancestor_table .= qq(<table border="1"><tr><th>steps</th><th>relationship</th><th>id</th><th>name</th></tr>\n);
  foreach my $ancestor (sort keys %ancestors) {
    next unless $ancestor;
#     my ($directNumFound, $inferredNumFound) = &getDirectInferredGenes($ancestor);
    my ($inferredLink) = &getInferredGenesHrefTarget($ancestor);	# raymond + chris don't care about gene counts for ancestors
#     my ($directLink)   = &getDirectGenesHrefTarget($ancestor);	# raymond + chris don't care about gene counts for ancestors
    my ($link_ancestor) = &makeLink($ancestor, $ancestor);
    my $ancestor_name = $label{$ancestor};
    my ($link_ancestorname) = &makeLink($ancestor, $ancestor_name);
#     my ($max_steps) = &getLongestPath( $ancestor, $focusTermId );		# most steps between ancestor and focusTermId
    my ($max_steps, $relationship) = &getLongestPathAndTransitivity( $ancestor, $focusTermId );	# given focusTermId and ancestor, get the longest path and dominant inferred transitivity
    my $indentation = $max_steps - 1; if ($indentation > $max_indent) { $max_indent = $indentation; }
    $inferredTree{$indentation}{qq($relationship : $link_ancestor $link_ancestorname [${inferredLink}])}++;	# raymond solr virtual server is really fast, added them back
#     $inferredTree{$indentation}{qq($relationship : $link_ancestor $link_ancestorname gene products: ${directLink}, ${inferredLink})}++;	# raymond + chris don't care about gene counts for ancestors
#     $inferredTree{$indentation}{qq($relationship : $link_ancestor $link_ancestorname)}++;	# raymond + chris don't care about gene counts for ancestors
    $ancestor_table .= qq(<tr><td>$max_steps</td><td>$relationship</td><td>$link_ancestor</td><td>$link_ancestorname</td></tr>\n);
  } # foreach my $ancestor (sort keys %ancestors)
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
#   my ($directNumFound, $inferredNumFound) = &getDirectInferredGenes($goid);
#   my ($inferredLink) = &getInferredGenesHrefTarget($goid);	# slow to get each count from its own url
#   my ($directLink)   = &getDirectGenesHrefTarget($goid);	# slow to get each count from its own url
#   my ($directGenesCountHashref)   = &getGenesCountHash($goid, 'direct');	# get hash of goid to direct genes count
  my ($inferredGenesCountHashref) = &getGenesCountHash($focusTermId, 'inferred');	# get hash of focusTermId to inferred genes count
#   my %directGenesCount   = %$directGenesCountHashref;
#   my $directLink   = &makeGenesLink($goid, $directGenesCount{$goid},   'direct');
  my %inferredGenesCount = %$inferredGenesCountHashref;
#   my $inferredLink = &makeGenesLink($goid, $inferredGenesCount{$goid}, 'inferred');
  my $inferredLink = &makeGenesLink($focusTermId, $inferredGenesCount{$focusTermId}, $label{$focusTermId});
#   print qq($spacer<span style="color:green">$goid : $label{$goid}</span> gene products: ${inferredLink}<br/>\n);	# add data for main term
  print qq($spacer<span style="color:green">$focusTermId : $label{$focusTermId}</span> [${inferredLink}]<br/>\n);	# add data for main term
  foreach my $child (sort keys %children) {			# for each child
#     my ($directNumFound, $inferredNumFound) = &getDirectInferredGenes($child);
#     my ($inferredLink) = &getInferredGenesHrefTarget($child);	# slow to get each count from its own url
#     my ($directLink) = &getDirectGenesHrefTarget($child);	# slow to get each count from its own url
#     my $directLink   = &makeGenesLink($child, $directGenesCount{$child},   'direct');
#     my $inferredLink = &makeGenesLink($child, $inferredGenesCount{$child}, 'inferred');
    my $inferredLink = &makeGenesLink($child, $inferredGenesCount{$child}, $label{$child});
    my $relationship = $children{$child};
    my ($link_child) = &makeLink($child, $child);		# make link to id
    my $child_name = $label{$child};
    my ($link_childname) = &makeLink($child, $child_name);	# make link to name
    for (1 .. $max_indent) { print $spacer; }			# add indentation for children term
    print $spacer . $spacer . qq($relationship : $link_child $link_childname [${inferredLink}]<br/>\n);	# add data for child
#     print $spacer . $spacer . qq($relationship : $link_child $link_childname gene products: ${inferredLink}<br/>\n);	# add data for child
  } # foreach my $child (sort keys %children)

  print qq(<br/><br/>\n);

  &treeExpand();
  
  &printHtmlFooter(); 
} # sub dag

sub makeGenesLink {				# give a focusTermId, number of genes for that focusTermId, and direct vs inferred ;  create a link to show the genes
#   my ($goid, $numFound, $directOrInferred) = @_;
  my ($focusTermId, $numFound, $focusTermName) = @_;		# always show inferred genes, not direct, and pass name of focusTermId
#   my $link = "0 $directOrInferred";		# by default there are zero of the given direct vs inferred
  my $link = "0 gene products";			# by default there are zero of the given direct vs inferred
  if ($numFound > 0) {				# if there's at least one gene, make the link to this CGI
#     $link = qq(<a target="new" href="amigo.cgi?action=showGenes&directOrInferred=$directOrInferred&goid=$goid">$numFound ($directOrInferred)</a>);
#     $link = qq(<a target="new" href="amigo.cgi?action=showGenes&focusTermName=$focusTermName&goid=$goid">$numFound (inferred)</a>);
    $link = qq(<a target="new" href="amigo.cgi?action=showGenes&focusTermName=$focusTermName&focusTermId=$focusTermId">$numFound gene products</a>); }
  return $link;
} # makeGenestLink

sub getGenesCountHash {				# for a given focusTermId, get the genes count of itself and its direct children, option direct or inferred genes
  my ($focusTermId, $directOrInferred) = @_;
  my %genesCount;				# count of genes for the given direct vs inferred
  my ($solr_url) = &getSolrUrl($focusTermId);
  my $url = $solr_url . 'select?qt=standard&indent=on&wt=json&version=2.2&fl=id&start=0&rows=10000000&q=document_category:bioentity&facet=true&facet.field=annotation_class_list&facet.limit=-1&facet.mincount=1&facet.prefix=GO&facet.sort=count&fq=source:%22WB%22&fq=annotation_class_list:%22' . $focusTermId . '%22';
# print "URL $url URL";		# currently not getting the right counts because facet_count->facet_fields->annotation_class_list is empty.  2013 11 09
  my $searchField = 'annotation_class_list';	# by default assume direct search for URL and JSON field
  if ($directOrInferred eq 'inferred') { 	# if inferred, change the URL and JSON field
    $searchField = 'regulates_closure';
    $url = $solr_url . 'select?qt=standard&indent=on&wt=json&version=2.2&fl=id&start=0&rows=10000000&q=document_category:bioentity&facet=true&facet.field=regulates_closure&facet.limit=-1&facet.mincount=1&facet.prefix=GO&facet.sort=count&fq=source:%22WB%22&fq=regulates_closure:%22' . $focusTermId . '%22'; }
  my $page_data = get $url;
  my $perl_scalar = $json->decode( $page_data );
  my %jsonHash = %$perl_scalar;

  $genesCount{$focusTermId} = $jsonHash{'response'}{'numFound'}; 	# get the main focusTermId gene count and store in %genesCount
  while (scalar @{ $jsonHash{'facet_counts'}{'facet_fields'}{$searchField} } > 0) {	# while there are pairs of genes/count in the JSON array
    my $focusTermId = shift @{ $jsonHash{'facet_counts'}{'facet_fields'}{$searchField} }; # get the focusTermId
    my $count = shift @{ $jsonHash{'facet_counts'}{'facet_fields'}{$searchField} }; 	# get the count
    $genesCount{$focusTermId} = $count;							# add the mapping to %genesCount
  } # while (scalar @{ $jsonHash{'facet_counts'}{'facet_fields'}{$searchField} } > 0)

  return \%genesCount;
} # sub getGenesCountHash

sub showGenes {					# page to show gene products linked to a focusTermId
  &printHtmlHeader(); 
  my ($var, $focusTermId) = &getHtmlVar($query, 'focusTermId');
#   my ($var, $directOrInferred) = &getHtmlVar($query, 'directOrInferred');
  my ($var, $focusTermName) = &getHtmlVar($query, 'focusTermName');
  my %url;
  my ($solr_url) = &getSolrUrl($focusTermId);
  $url{"direct"} = $solr_url . 'select?qt=standard&indent=on&wt=json&version=2.2&fl=id&start=0&rows=10000000&q=document_category:bioentity&fq=source:%22WB%22&fq=%7B!cache=false%7Dannotation_class_list:%22'. $focusTermId . '%22';	# with wbgenes listed, more specific q, cache off
  $url{"inferred"} = $solr_url . 'select?qt=standard&indent=on&wt=json&version=2.2&fl=id&start=0&rows=10000000&q=document_category:bioentity&fq=source:%22WB%22&fq=%7B!cache=false%7Dregulates_closure:%22' . $focusTermId . '%22';	# with wbgenes listed, more specific q, cache off
  foreach my $type (sort keys %url) {
    my $url = $url{$type};
    my $page = get $url; my $numFound = 0; my @genes;
    if ($page =~ m/"numFound":(\d+),/) { $numFound = $1; }
    if ($numFound > 0) {							# if there are genes to show
      if ($type eq 'direct') {				# direct have one message
          print qq(List of $numFound genes that were annotated with $focusTermId $focusTermName.<br/>\n); }
        elsif ($type eq 'inferred') {				# inferred have another message
          print qq(List of $numFound genes that were annotated with $focusTermId $focusTermName or any of its transitive descendant terms.<br/>\n); }
      (@genes) = $page =~ m/"id":"WB:(WBGene\d+)"/g;			# gene the genes
      foreach my $gene (sort @genes) { print qq($gene<br/>\n); }		# and list the genes
    } # if ($numFound > 0)
    print qq(<br/>\n);
  } # foreach my $type (sort keys %url)
    

#   my $url = 'http://golr.berkeleybop.org/select?qt=standard&indent=on&wt=json&version=2.2&fl=id&start=0&rows=10000000&q=document_category:bioentity&fq=source:%22WB%22&fq=%7B!cache=false%7Dannotation_class_list:%22'. $goid . '%22';	# with wbgenes listed, more specific q, cache off
#   if ($directOrInferred eq 'inferred') {
#     $url = 'http://golr.berkeleybop.org/select?qt=standard&indent=on&wt=json&version=2.2&fl=id&start=0&rows=10000000&q=document_category:bioentity&fq=source:%22WB%22&fq=%7B!cache=false%7Dregulates_closure:%22' . $goid . '%22'; }	# with wbgenes listed, more specific q, cache off
#   my $page = get $url; my $numFound = 0; my @genes;
#   if ($page =~ m/"numFound":(\d+),/) { $numFound = $1; }
#   if ($numFound > 0) {							# if there are genes to show
#     if ($directOrInferred eq 'direct') {				# direct have one message
#         print qq(List of $numFound genes that were annotated with $goid .<br/>\n); }
#       elsif ($directOrInferred eq 'inferred') {				# inferred have another message
#         print qq(List of $numFound genes that were annotated with $goid or any of its transitive descendant terms.<br/>\n); }
#     (@genes) = $page =~ m/"id":"WB:(WBGene\d+)"/g;			# gene the genes
#     foreach my $gene (sort @genes) { print qq($gene<br/>\n); }		# and list the genes
#   } # if ($numFound > 0)
  &printHtmlFooter(); 
} # sub showGenes

sub getLongestPathAndTransitivity {			# given two nodes, get the longest path and dominant inferred transitivity
  my ($ancestor, $focusTermId) = @_;					# the ancestor and focusTermId from which to find the longest path
  &recurseLongestPath($focusTermId, $focusTermId, $ancestor, $focusTermId);	# recurse to find longest path given current, start, end, and list of current path
  my $max_nodes = 0;							# the most nodes found among all paths travelled
  my %each_finalpath_transitivity;					# hash of inferred sensitivity value for each path that finished
  foreach my $finpath (@{ $paths{"finalpath"} }) {			# for each of the paths that reached the end node
    my $nodes = scalar @$finpath;					# amount of nodes in the path
    if ($nodes > $max_nodes) { $max_nodes = $nodes; }			# if more nodes than max, set new max

    my $child = shift @$finpath; my $parent = shift @$finpath;		# get first node and its parent along this path
    my $relationship_one = $paths{"childToParent"}{$child}{$parent};	# get relationship between them (from json)
    my $relationship_two = '';						# initialize relationship between parent and its parent 
    while (scalar @$finpath > 0) {					# while there are steps in the path
      $child = $parent;							# the child in the new step is the previous parent
      $parent = shift @$finpath;					# the new parent is the next node in the path
      $relationship_two = $paths{"childToParent"}{$child}{$parent};	# the second relationship is the relationship between this pair
      $relationship_one = &getInferredRelationship($relationship_one, $relationship_two); 	# get inferred relationship given those two relationships
    }
    $each_finalpath_transitivity{$relationship_one}++;			# add final inferred transitivity relationship to hash
  } # foreach my $finpath (@finalpath)
  delete $paths{"finalpath"};						# reset finalpath for other ancestors
  my $max_steps = $max_nodes - 1;					# amount of steps is one less than amount of nodes

  my %transitivity_priority;						# when different paths have different inferred transitivity, highest number takes precedence
  $transitivity_priority{"is_a"}                 = 1;
  $transitivity_priority{"has_part"}             = 2;
  $transitivity_priority{"part_of"}              = 3;
  $transitivity_priority{"regulates"}            = 4;
  $transitivity_priority{"positively_regulates"} = 5;
  $transitivity_priority{"negatively_regulates"} = 6;
  $transitivity_priority{"occurs_in"}            = 7;
  $transitivity_priority{"unknown"}              = 8;			# in case some relationship or pair of relationships is unaccounted for
  my @all_inferred_paths_transitivity = sort { $transitivity_priority{$b} <=> $transitivity_priority{$a} } keys %each_finalpath_transitivity ;
									# sort all inferred transitivities by highest precedence
  my $dominant_inferred_transitivity = shift @all_inferred_paths_transitivity;	# dominant is the one with highest precedence
  return ($max_steps, $dominant_inferred_transitivity);			# return the maximum number of steps and dominant inferred transitivity
# my ($relationship) = &getInferredRelationship($one, $two); 
} # sub getLongestPathAndTransitivity 

sub recurseLongestPath {
  my ($current, $start, $end, $curpath) = @_;				# current node, starting node, end node, path travelled so far
  foreach my $parent (sort keys %{ $paths{"childToParent"}{$current} }) {	# for each parent of the current node
    my @curpath = split/\t/, $curpath;					# convert current path to array
    push @curpath, $parent;						# add the current parent
    if ($parent eq $end) {						# if current parent is the end node
        my @tmpWay = @curpath;						# make a copy of the array
        push @{ $paths{"finalpath"} }, \@tmpWay; }			# put a reference to the array copy into the finalpath
      else {								# not the end node yet
        my $curpath = join"\t", @curpath;				# pass literal current path instead of reference
        &recurseLongestPath($parent, $start, $end, $curpath); }		# recurse to keep looking for the final node
  } # foreach $parent (sort keys %{ $paths{"childToParent"}{$current} })
} # sub recurseLongestPath

sub getInferredRelationship {
  my ($one, $two) = @_; my $relationship = 'unknown';
  if ($one eq 'is_a') { 
      if ($two eq 'is_a') {                     $relationship = 'is_a';                  }
      elsif ($two eq 'part_of') {               $relationship = 'part_of';               }
      elsif ($two eq 'regulates') {             $relationship = 'regulates';             }
      elsif ($two eq 'positively_regulates') {  $relationship = 'positively_regulates';  }
      elsif ($two eq 'negatively_regulates') {  $relationship = 'negatively_regulates';  }
      elsif ($two eq 'has_part') {              $relationship = 'has_part';              } }
    elsif ($one eq 'part_of') { 
      if ($two eq 'is_a') {                     $relationship = 'part_of';               }
      elsif ($two eq 'part_of') {               $relationship = 'part_of';               } }
    elsif ($one eq 'regulates') { 
      if ($two eq 'is_a') {                     $relationship = 'regulates';             }
      elsif ($two eq 'part_of') {               $relationship = 'regulates';             } }
    elsif ($one eq 'positively_regulates') { 
      if ($two eq 'is_a') {                     $relationship = 'positively_regulates';  }
      elsif ($two eq 'part_of') {               $relationship = 'regulates';             } }
    elsif ($one eq 'negatively_regulates') { 
      if ($two eq 'is_a') {                     $relationship = 'negatively_regulates';  }
      elsif ($two eq 'part_of') {               $relationship = 'regulates';             } }
    elsif ($one eq 'has_part') { 
      if ($two eq 'is_a') {                     $relationship = 'has_part';              }
      elsif ($two eq 'has_part') {              $relationship = 'has_part';              } }
  return $relationship;
} # sub getInferredRelationship

sub makeLink {
  my ($focusTermId, $text) = @_;
  my $url = "amigo.cgi?action=Tree&focusTermId=$focusTermId";
  my $link = qq(<a href="$url">$text</a>);
  return $link;
} # sub makeLink

sub printHtmlFooter { print qq(</body></html>\n); }

sub printHtmlHeader { 
  my $javascript = << "EndOfText";
<script src="http://code.jquery.com/jquery-1.9.1.js"></script>
<script src="amigo.js"></script>
<script type="text/javascript">
function toggleShowHide(element) {
    document.getElementById(element).style.display = (document.getElementById(element).style.display == "none") ? "" : "none";
    return false;
}
function togglePlusMinus(element) {
    document.getElementById(element).innerHTML = (document.getElementById(element).innerHTML == "&nbsp;+&nbsp;") ? "&nbsp;-&nbsp;" : "&nbsp;+&nbsp;";
    return false;
}
</script>
EndOfText
  print qq(Content-type: text/html\n\n<html><head><title>Amigo testing</title>$javascript</head><body>\n); }

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


# invidividual page search for each set of counts (very slow)
# sub getInferredGenesHrefTarget { return ('1 testing'); }
# sub getDirectGenesHrefTarget { return ('2 testing'); }
# REVERT
sub getInferredGenesHrefTarget {
  my ($focusTermId) = @_;
  my ($solr_url) = &getSolrUrl($focusTermId);
  my $inferredUrl = $solr_url . 'select?qt=standard&indent=on&wt=json&version=2.2&fl=%2Cscore&fq=&q=*:*&fq=document_category:%22bioentity%22&fq=source:%22WB%22&fq=regulates_closure:%22' . $focusTermId . '%22';	# just the numFound
  my $inferredPage = get $inferredUrl; my $inferredNumFound = 0; 
  if ($inferredPage =~ m/"numFound":(\d+),/) { $inferredNumFound = $1; }
#   my $inferredLink = '0 (direct+inferred)';
  my $inferredLink = '0 gene products';
  if ($inferredNumFound > 0) {
#     $inferredLink = qq(<a target="new" href="amigo.cgi?action=showInferredGenes&focusTermId=$focusTermId">$inferredNumFound (direct+inferred)</a>);
    $inferredLink = qq(<a target="new" href="amigo.cgi?action=showInferredGenes&focusTermId=$focusTermId">$inferredNumFound gene products</a>); }
  return $inferredLink;
} # sub getInferredGenesHrefTarget

# sub getDirectGenesHrefTarget {
#   my ($goid) = @_;
#   my ($solr_url) = &getSolrUrl($goid);
#   my $directUrl = $solr_url . 'select?qt=standard&indent=on&wt=json&version=2.2&fl=id%2Cscore&fq=&q=*:*&fq=document_category:%22bioentity%22&fq=source:%22WB%22&fq=annotation_class_list:%22' . $goid . '%22';	# just the numFound
#   my $directPage = get $directUrl; my $directNumFound = 0; 
#   if ($directPage =~ m/"numFound":(\d+),/) { $directNumFound = $1; }
#   my $directLink = '0 (direct)';
#   if ($directNumFound > 0) {
#     $directLink = qq(<a target="new" href="amigo.cgi?action=showDirectGenes&goid=$goid">$directNumFound (direct)</a>); }
#   return $directLink;
# } # sub getDirectGenesHrefTarget


__END__

Given a node in a parent-child table, follow it to find all edges and paths to ancestors.
http://stackoverflow.com/questions/1144827/sql-find-all-direct-descendants-in-a-tree
WITH RECURSIVE q AS
        (
        SELECT  h, 1 AS level, ARRAY[goid_parent] AS breadcrumb
        FROM    obo_goid_edges h
        WHERE   goid_child = 'GO:0010610'
        UNION ALL
        SELECT  hi, q.level + 1 AS level, breadcrumb || goid_parent
        FROM    q
        JOIN    obo_goid_edges hi
        ON      hi.goid_child = (q.h).goid_parent
        )
SELECT  REPEAT('  ', level) || (q.h).goid_parent,
        (q.h).goid_child,
        (q.h).goid_parent,
        (q.h).relationship,
        level,
        breadcrumb::VARCHAR AS path
FROM    q
ORDER BY
        breadcrumb

           ?column?           | goid_child | goid_parent | relationship | level |                                                 path                          
------------------------------+------------+-------------+--------------+-------+------------------------------------------------------------------------------------------------------
   GO:0033554                 | GO:0010610 | GO:0033554  | part_of      |     1 | {GO:0033554}
     GO:0006950               | GO:0033554 | GO:0006950  | is_a         |     2 | {GO:0033554,GO:0006950}
       GO:0050896             | GO:0006950 | GO:0050896  | is_a         |     3 | {GO:0033554,GO:0006950,GO:0050896}
         GO:0008150           | GO:0050896 | GO:0008150  | is_a         |     4 | {GO:0033554,GO:0006950,GO:0050896,GO:0008150}
     GO:0051716               | GO:0033554 | GO:0051716  | is_a         |     2 | {GO:0033554,GO:0051716}
       GO:0044763             | GO:0051716 | GO:0044763  | is_a         |     3 | {GO:0033554,GO:0051716,GO:0044763}
         GO:0009987           | GO:0044763 | GO:0009987  | is_a         |     4 | {GO:0033554,GO:0051716,GO:0044763,GO:0009987}
           GO:0008150         | GO:0009987 | GO:0008150  | is_a         |     5 | {GO:0033554,GO:0051716,GO:0044763,GO:0009987,GO:0008150}
         GO:0044699           | GO:0044763 | GO:0044699  | is_a         |     4 | {GO:0033554,GO:0051716,GO:0044763,GO:0044699}
           GO:0008150         | GO:0044699 | GO:0008150  | is_a         |     5 | {GO:0033554,GO:0051716,GO:0044763,GO:0044699,GO:0008150}
       GO:0050896             | GO:0051716 | GO:0050896  | is_a         |     3 | {GO:0033554,GO:0051716,GO:0050896}
         GO:0008150           | GO:0050896 | GO:0008150  | is_a         |     4 | {GO:0033554,GO:0051716,GO:0050896,GO:0008150}
   GO:0043488                 | GO:0010610 | GO:0043488  | is_a         |     1 | {GO:0043488}
     GO:0043487               | GO:0043488 | GO:0043487  | is_a         |     2 | {GO:0043488,GO:0043487}
       GO:0010608             | GO:0043487 | GO:0010608  | is_a         |     3 | {GO:0043488,GO:0043487,GO:0010608}
         GO:0010468           | GO:0010608 | GO:0010468  | is_a         |     4 | {GO:0043488,GO:0043487,GO:0010608,GO:0010468}
           GO:0010467         | GO:0010468 | GO:0010467  | regulates    |     5 | {GO:0043488,GO:0043487,GO:0010608,GO:0010468,GO:0010467}
             GO:0043170       | GO:0010467 | GO:0043170  | is_a         |     6 | {GO:0043488,GO:0043487,GO:0010608,GO:0010468,GO:0010467,GO:0043170}
               GO:0071704     | GO:0043170 | GO:0071704  | is_a         |     7 | {GO:0043488,GO:0043487,GO:0010608,GO:0010468,GO:0010467,GO:0043170,GO:0071704}
                 GO:0008152   | GO:0071704 | GO:0008152  | is_a         |     8 | {GO:0043488,GO:0043487,GO:0010608,GO:0010468,GO:0010467,GO:0043170,GO:0071704,GO:0008152}
                   GO:0008150 | GO:0008152 | GO:0008150  | is_a         |     9 | {GO:0043488,GO:0043487,GO:0010608,GO:0010468,GO:0010467,GO:0043170,GO:0071704,GO:0008152,GO:0008150}
           GO:0060255         | GO:0010468 | GO:0060255  | is_a         |     5 | {GO:0043488,GO:0043487,GO:0010608,GO:0010468,GO:0060255}
             GO:0019222       | GO:0060255 | GO:0019222  | is_a         |     6 | {GO:0043488,GO:0043487,GO:0010608,GO:0010468,GO:0060255,GO:0019222}
               GO:0008152     | GO:0019222 | GO:0008152  | regulates    |     7 | {GO:0043488,GO:0043487,GO:0010608,GO:0010468,GO:0060255,GO:0019222,GO:0008152}
                 GO:0008150   | GO:0008152 | GO:0008150  | is_a         |     8 | {GO:0043488,GO:0043487,GO:0010608,GO:0010468,GO:0060255,GO:0019222,GO:0008152,GO:0008150}
               GO:0050789     | GO:0019222 | GO:0050789  | is_a         |     7 | {GO:0043488,GO:0043487,GO:0010608,GO:0010468,GO:0060255,GO:0019222,GO:0050789}
                 GO:0008150   | GO:0050789 | GO:0008150  | regulates    |     8 | {GO:0043488,GO:0043487,GO:0010608,GO:0010468,GO:0060255,GO:0019222,GO:0050789,GO:0008150}
                 GO:0065007   | GO:0050789 | GO:0065007  | is_a         |     8 | {GO:0043488,GO:0043487,GO:0010608,GO:0010468,GO:0060255,GO:0019222,GO:0050789,GO:0065007}
                   GO:0008150 | GO:0065007 | GO:0008150  | is_a         |     9 | {GO:0043488,GO:0043487,GO:0010608,GO:0010468,GO:0060255,GO:0019222,GO:0050789,GO:0065007,GO:0008150}
             GO:0043170       | GO:0060255 | GO:0043170  | regulates    |     6 | {GO:0043488,GO:0043487,GO:0010608,GO:0010468,GO:0060255,GO:0043170}
               GO:0071704     | GO:0043170 | GO:0071704  | is_a         |     7 | {GO:0043488,GO:0043487,GO:0010608,GO:0010468,GO:0060255,GO:0043170,GO:0071704}
                 GO:0008152   | GO:0071704 | GO:0008152  | is_a         |     8 | {GO:0043488,GO:0043487,GO:0010608,GO:0010468,GO:0060255,GO:0043170,GO:0071704,GO:0008152}
                   GO:0008150 | GO:0008152 | GO:0008150  | is_a         |     9 | {GO:0043488,GO:0043487,GO:0010608,GO:0010468,GO:0060255,GO:0043170,GO:0071704,GO:0008152,GO:0008150}
       GO:0065008             | GO:0043487 | GO:0065008  | is_a         |     3 | {GO:0043488,GO:0043487,GO:0065008}
         GO:0065007           | GO:0065008 | GO:0065007  | is_a         |     4 | {GO:0043488,GO:0043487,GO:0065008,GO:0065007}
           GO:0008150         | GO:0065007 | GO:0008150  | is_a         |     5 | {GO:0043488,GO:0043487,GO:0065008,GO:0065007,GO:0008150}
(36 rows)





# transitivity :
# i  + i  = i
# i  + p  = p 
# i  + r  = r 
# i  + r+ = r+
# i  + r- = r-
# i  + hp = hp
# p  + i  = p
# p  + p  = p
# r  + i  = r
# r  + p  = r
# r+ + i  = r+
# r+ + p  = r
# r- + i  = r-
# r- + p  = r
# hp + i  = hp
# hp + hp = hp

# separate routines to do the same thing with different URLs and messages
# sub showInferredGenes {					# page to show gene products linked to a goid
#   &printHtmlHeader(); 
#   my ($var, $goid) = &getHtmlVar($query, 'goid');
#   my $inferredUrl = 'http://golr.berkeleybop.org/select?qt=standard&indent=on&wt=json&version=2.2&fl=id&start=0&rows=10000000&q=document_category:bioentity&fq=source:%22WB%22&fq=%7B!cache=false%7Dregulates_closure:%22' . $goid . '%22';	# with wbgenes listed, more specific q, cache off
# # http://golr.berkeleybop.org/select?qt=standard&indent=on&wt=json&version=2.2&fl=id&start=0&rows=10000000&fq=&q=*:*&fq=document_category:%22bioentity%22&fq=source:%22WB%22&fq=regulates_closure:%22' . $goid . '%22';
#   my $inferredPage = get $inferredUrl; my $inferredNumFound = 0; my @genes;
#   if ($inferredPage =~ m/"numFound":(\d+),/) { $inferredNumFound = $1; }
#   if ($inferredNumFound > 0) {
#     print qq(List of $inferredNumFound genes that were annotated with $goid or any of its transitive descendant terms.<br/>\n);
#     (@genes) = $inferredPage =~ m/"id":"WB:(WBGene\d+)"/g;
#     foreach my $gene (sort @genes) { print qq($gene<br/>\n); }
#   }
#   &printHtmlFooter(); 
# } # sub showInferredGenes
# sub showDirectGenes {					# page to show gene products linked to a goid
#   &printHtmlHeader(); 
#   my ($var, $goid) = &getHtmlVar($query, 'goid');
#   my $inferredUrl = 'http://golr.berkeleybop.org/select?qt=standard&indent=on&wt=json&version=2.2&fl=id&start=0&rows=10000000&q=document_category:bioentity&fq=source:%22WB%22&fq=%7B!cache=false%7Dannotation_class_list:%22'. $goid . '%22';	# with wbgenes listed, more specific q, cache off
#   my $inferredPage = get $inferredUrl; my $inferredNumFound = 0; my @genes;
#   if ($inferredPage =~ m/"numFound":(\d+),/) { $inferredNumFound = $1; }
#   if ($inferredNumFound > 0) {
#     print qq(List of $inferredNumFound genes that were annotated with $goid .<br/>\n);
#     (@genes) = $inferredPage =~ m/"id":"WB:(WBGene\d+)"/g;
#     foreach my $gene (sort @genes) { print qq($gene<br/>\n); }
#   }
#   &printHtmlFooter(); 
# } # sub showDirectGenes




# parent to child
# sub getLongestPath {
#   my ($ancestor, $goid) = @_;						# the ancestor and goid from which to find the longest path
#   &recurseLongestPath($ancestor, $ancestor, $goid, $ancestor);		# recurse to find longest path given current, start, end, and list of current path
#   my $max_nodes = 0;							# the most nodes found among all paths travelled
#   foreach my $finpath (@{ $paths{"finalpath"} }) {			# for each of the paths that reached the end node
#     my $nodes = scalar @$finpath;					# amount of nodes in the path
#     if ($nodes > $max_nodes) { $max_nodes = $nodes; }			# if more nodes than max, set new max
#   } # foreach my $finpath (@finalpath)
#   delete $paths{"finalpath"};						# reset finalpath for other ancestors
#   my $max_steps = $max_nodes - 1;					# amount of steps is one less than amount of nodes
#   return $max_steps;
# } # sub getLongestPath 
# 
# sub recurseLongestPath {
#   my ($current, $start, $end, $curpath) = @_;				# current node, starting node, end node, path travelled so far
#   foreach my $child (sort keys %{ $paths{"parentToChild"}{$current} }) {	# for each child of the current node
#     my @curpath = split/\t/, $curpath;					# convert current path to array
#     push @curpath, $child;						# add the current child
#     if ($child eq $end) {						# if current child is the end node
#         my @tmpWay = @curpath;						# make a copy of the array
#         push @{ $paths{"finalpath"} }, \@tmpWay; }			# put a reference to the array copy into the finalpath
#       else {								# not the end node yet
#         my $curpath = join"\t", @curpath;				# pass literal current path instead of reference
#         &recurseLongestPath($child, $start, $end, $curpath); }		# recurse to keep looking for the final node
#   } # foreach $child (sort keys %{ $paths{"parentToChild"}{$current} })
# } # sub recurseLongestPath


sub getInferredGenesDynamicSpan {	# takes too long to load all values for all links just to hide most of them anyway
  my ($ancestor) = @_;
#   my $inferredUrl = 'http://golr.berkeleybop.org/select?qt=standard&indent=on&wt=json&version=2.2&fl=*%2Cscore&fq=&q=*:*&fq=document_category:%22bioentity%22&fq=source:%22WB%22&fq=regulates_closure:%22' . $ancestor . '%22';
#   my $inferredUrl = 'http://golr.berkeleybop.org/select?qt=standard&indent=on&wt=json&version=2.2&fl=%2Cscore&fq=&q=*:*&fq=document_category:%22bioentity%22&fq=source:%22WB%22&fq=regulates_closure:%22' . $ancestor . '%22';	# just the numFound
  my $inferredUrl = 'http://golr.berkeleybop.org/select?qt=standard&indent=on&wt=json&version=2.2&fl=id&start=0&rows=10000000&fq=&q=*:*&fq=document_category:%22bioentity%22&fq=source:%22WB%22&fq=regulates_closure:%22' . $ancestor . '%22';
# print "URL $inferredUrl URL<br>";
  my $inferredPage = get $inferredUrl; my $inferredNumFound = 0; my @genes;
  if ($inferredPage =~ m/"numFound":(\d+),/) { $inferredNumFound = $1; }
  my $inferredLink = '[0 gene products]';
  if ($inferredNumFound > 0) {
    (@genes) = $inferredPage =~ m/"id":"WB:(WBGene\d+)"/g;
    my $genes = join" ", @genes;
#     my $ancestor_go = $ancestor; $ancestor_go =~ s/://g;
    $inferredLink = qq([<span style="text-decoration: underline; color: blue; cursor: pointer;" onclick="toggleShowHide('genes_$ancestor');">$inferredNumFound gene products</span>]<span id="genes_$ancestor" style="display: none">$genes</span>); }
  return $inferredLink;
} # sub getInferredGenesDynamicSpan

sub FAKEgetDirectInferredGenes { return ('1', '2'); } 
sub getDirectInferredGenes {		# was getting both sets first, then switched to just one set, back to both sets, but just keeping it separate for ease
  my ($ancestor) = @_;
  my $directUrl = 'http://golr.berkeleybop.org/select?qt=standard&indent=on&wt=json&version=2.2&fl=*%2Cscore&fq=&q=*:*&fq=document_category:%22bioentity%22&fq=source:%22WB%22&fq=annotation_class_list:%22' . $ancestor . '%22';
  my $directPage = get $directUrl; my $directNumFound = 0;
  if ($directPage =~ m/"numFound":(\d+),/) { $directNumFound = $1; }
#   my $inferredUrl = 'http://golr.berkeleybop.org/select?qt=standard&indent=on&wt=json&version=2.2&fl=*%2Cscore&fq=&q=*:*&fq=document_category:%22bioentity%22&fq=source:%22WB%22&fq=regulates_closure:%22' . $ancestor . '%22';
  my $inferredUrl = 'http://golr.berkeleybop.org/select?qt=standard&indent=on&wt=json&version=2.2&fl=%2Cscore&fq=&q=*:*&fq=document_category:%22bioentity%22&fq=source:%22WB%22&fq=regulates_closure:%22' . $ancestor . '%22';
  my $inferredPage = get $inferredUrl; my $inferredNumFound = 0;
  if ($inferredPage =~ m/"numFound":(\d+),/) { $inferredNumFound = $1; }
  return ($directNumFound, $inferredNumFound);
} # sub getDirectInferredGenes
    


        "regulates_transitivity_graph_json":"{\"nodes\":[{\"id\":\"GO:0019222\",\"lbl\":\"regulation of metabolic process\"},{\"id\":\"GO:0043487\",\"lbl\":\"regulation of RNA stability\"},{\"id\":\"GO:0044763\",\"lbl\":\"single-organism cellular process\"},{\"id\":\"GO:0043488\",\"lbl\":\"regulation of mRNA stability\"},{\"id\":\"GO:0009987\",\"lbl\":\"cellular process\"},{\"id\":\"GO:0044699\",\"lbl\":\"single-organism process\"},{\"id\":\"GO:0065007\",\"lbl\":\"biological regulation\"},{\"id\":\"GO:0006950\",\"lbl\":\"response to stress\"},{\"id\":\"GO:0065008\",\"lbl\":\"regulation of biological quality\"},{\"id\":\"GO:0008152\",\"lbl\":\"metabolic process\"},{\"id\":\"GO:0033554\",\"lbl\":\"cellular response to stress\"},{\"id\":\"GO:0060255\",\"lbl\":\"regulation of macromolecule metabolic process\"},{\"id\":\"GO:0008150\",\"lbl\":\"biological_process\"},{\"id\":\"GO:0050896\",\"lbl\":\"response to stimulus\"},{\"id\":\"GO:0010608\",\"lbl\":\"posttranscriptional regulation of gene expression\"},{\"id\":\"GO:0051716\",\"lbl\":\"cellular response to stimulus\"},{\"id\":\"GO:0010610\",\"lbl\":\"regulation of mRNA stability involved in response to stress\"},{\"id\":\"GO:0050789\",\"lbl\":\"regulation of biological process\"},{\"id\":\"GO:0010467\",\"lbl\":\"gene expression\"},{\"id\":\"GO:0010468\",\"lbl\":\"regulation of gene expression\"},{\"id\":\"GO:0043170\",\"lbl\":\"macromolecule metabolic process\"},{\"id\":\"GO:0071704\",\"lbl\":\"organic substance metabolic process\"}],\"edges\":[{\"sub\":\"GO:0010610\",\"obj\":\"GO:0006950\",\"pred\":\"part_of\"},{\"sub\":\"GO:0010610\",\"obj\":\"GO:0044699\",\"pred\":\"part_of\"},{\"sub\":\"GO:0010610\",\"obj\":\"GO:0065007\",\"pred\":\"is_a\"},{\"sub\":\"GO:0010610\",\"obj\":\"GO:0009987\",\"pred\":\"part_of\"},{\"sub\":\"GO:0010610\",\"obj\":\"GO:0043170\",\"pred\":\"is_a\"},{\"sub\":\"GO:0010610\",\"obj\":\"GO:0010467\",\"pred\":\"is_a\"},{\"sub\":\"GO:0010610\",\"obj\":\"GO:0019222\",\"pred\":\"is_a\"},{\"sub\":\"GO:0010610\",\"obj\":\"GO:0008150\",\"pred\":\"is_a\"},{\"sub\":\"GO:0010610\",\"obj\":\"GO:0043170\",\"pred\":\"regulates\"},{\"sub\":\"GO:0010610\",\"obj\":\"GO:0008150\",\"pred\":\"regulates\"},{\"sub\":\"GO:0010610\",\"obj\":\"GO:0010608\",\"pred\":\"is_a\"},{\"sub\":\"GO:0010610\",\"obj\":\"GO:0006950\",\"pred\":\"is_a\"},{\"sub\":\"GO:0010610\",\"obj\":\"GO:0008152\",\"pred\":\"is_a\"},{\"sub\":\"GO:0010610\",\"obj\":\"GO:0008152\",\"pred\":\"regulates\"},{\"sub\":\"GO:0010610\",\"obj\":\"GO:0033554\",\"pred\":\"part_of\"},{\"sub\":\"GO:0010610\",\"obj\":\"GO:0008150\",\"pred\":\"part_of\"},{\"sub\":\"GO:0010610\",\"obj\":\"GO:0010467\",\"pred\":\"regulates\"},{\"sub\":\"GO:0010610\",\"obj\":\"GO:0050896\",\"pred\":\"part_of\"},{\"sub\":\"GO:0010610\",\"obj\":\"GO:0060255\",\"pred\":\"is_a\"},{\"sub\":\"GO:0010610\",\"obj\":\"GO:0071704\",\"pred\":\"regulates\"},{\"sub\":\"GO:0010610\",\"obj\":\"GO:0010468\",\"pred\":\"is_a\"},{\"sub\":\"GO:0010610\",\"obj\":\"GO:0050789\",\"pred\":\"is_a\"},{\"sub\":\"GO:0010610\",\"obj\":\"GO:0043487\",\"pred\":\"is_a\"},{\"sub\":\"GO:0010610\",\"obj\":\"GO:0065008\",\"pred\":\"is_a\"},{\"sub\":\"GO:0010610\",\"obj\":\"GO:0033554\",\"pred\":\"is_a\"},{\"sub\":\"GO:0010610\",\"obj\":\"GO:0043488\",\"pred\":\"is_a\"},{\"sub\":\"GO:0010610\",\"obj\":\"GO:0044763\",\"pred\":\"part_of\"},{\"sub\":\"GO:0010610\",\"obj\":\"GO:0051716\",\"pred\":\"part_of\"}]}",

 "topology_graph_json":"{\"nodes\":[{\"id\":\"GO:0019222\",\"lbl\":\"regulation of metabolic process\"},{\"id\":\"GO:0043487\",\"lbl\":\"regulation of RNA stability\"},{\"id\":\"GO:0044763\",\"lbl\":\"single-organism cellular process\"},{\"id\":\"GO:0009987\",\"lbl\":\"cellular process\"},{\"id\":\"GO:0043488\",\"lbl\":\"regulation of mRNA stability\"},{\"id\":\"GO:0044699\",\"lbl\":\"single-organism process\"},{\"id\":\"GO:0006950\",\"lbl\":\"response to stress\"},{\"id\":\"GO:0065007\",\"lbl\":\"biological regulation\"},{\"id\":\"GO:0065008\",\"lbl\":\"regulation of biological quality\"},{\"id\":\"GO:2000815\",\"lbl\":\"regulation of mRNA stability involved in response to oxidative stress\"},{\"id\":\"GO:0008152\",\"lbl\":\"metabolic process\"},{\"id\":\"GO:0060255\",\"lbl\":\"regulation of macromolecule metabolic process\"},{\"id\":\"GO:0008150\",\"lbl\":\"biological_process\"},{\"id\":\"GO:0033554\",\"lbl\":\"cellular response to stress\"},{\"id\":\"GO:0050896\",\"lbl\":\"response to stimulus\"},{\"id\":\"GO:0010608\",\"lbl\":\"posttranscriptional regulation of gene expression\"},{\"id\":\"GO:0010610\",\"lbl\":\"regulation of mRNA stability involved in response to stress\"},{\"id\":\"GO:0051716\",\"lbl\":\"cellular response to stimulus\"},{\"id\":\"GO:0050789\",\"lbl\":\"regulation of biological process\"},{\"id\":\"GO:0010467\",\"lbl\":\"gene expression\"},{\"id\":\"GO:0010468\",\"lbl\":\"regulation of gene expression\"},{\"id\":\"GO:0043170\",\"lbl\":\"macromolecule metabolic process\"},{\"id\":\"GO:0071704\",\"lbl\":\"organic substance metabolic process\"}],\"edges\":[{\"sub\":\"GO:0006950\",\"obj\":\"GO:0050896\",\"pred\":\"is_a\"},{\"sub\":\"GO:0051716\",\"obj\":\"GO:0050896\",\"pred\":\"is_a\"},{\"sub\":\"GO:0010610\",\"obj\":\"GO:0006950\",\"pred\":\"part_of\"},{\"sub\":\"GO:0019222\",\"obj\":\"GO:0008152\",\"pred\":\"regulates\"},{\"sub\":\"GO:0033554\",\"obj\":\"GO:0006950\",\"pred\":\"is_a\"},{\"sub\":\"GO:0019222\",\"obj\":\"GO:0050789\",\"pred\":\"is_a\"},{\"sub\":\"GO:0010468\",\"obj\":\"GO:0060255\",\"pred\":\"is_a\"},{\"sub\":\"GO:0043170\",\"obj\":\"GO:0071704\",\"pred\":\"is_a\"},{\"sub\":\"GO:0050789\",\"obj\":\"GO:0065007\",\"pred\":\"is_a\"},{\"sub\":\"GO:0043487\",\"obj\":\"GO:0010608\",\"pred\":\"is_a\"},{\"sub\":\"GO:0050896\",\"obj\":\"GO:0008150\",\"pred\":\"is_a\"},{\"sub\":\"GO:0050789\",\"obj\":\"GO:0008150\",\"pred\":\"regulates\"},{\"sub\":\"GO:0044763\",\"obj\":\"GO:0044699\",\"pred\":\"is_a\"},{\"sub\":\"GO:0010610\",\"obj\":\"GO:0033554\",\"pred\":\"part_of\"},{\"sub\":\"GO:0008152\",\"obj\":\"GO:0008150\",\"pred\":\"is_a\"},{\"sub\":\"GO:0071704\",\"obj\":\"GO:0008152\",\"pred\":\"is_a\"},{\"sub\":\"GO:0010468\",\"obj\":\"GO:0010467\",\"pred\":\"regulates\"},{\"sub\":\"GO:0043487\",\"obj\":\"GO:0065008\",\"pred\":\"is_a\"},{\"sub\":\"GO:0065007\",\"obj\":\"GO:0008150\",\"pred\":\"is_a\"},{\"sub\":\"GO:0010468\",\"obj\":\"GO:0065007\",\"pred\":\"is_a\"},{\"sub\":\"GO:0065008\",\"obj\":\"GO:0065007\",\"pred\":\"is_a\"},{\"sub\":\"GO:0010608\",\"obj\":\"GO:0010468\",\"pred\":\"is_a\"},{\"sub\":\"GO:0060255\",\"obj\":\"GO:0019222\",\"pred\":\"is_a\"},{\"sub\":\"GO:0010467\",\"obj\":\"GO:0043170\",\"pred\":\"is_a\"},{\"sub\":\"GO:0044699\",\"obj\":\"GO:0008150\",\"pred\":\"is_a\"},{\"sub\":\"GO:0060255\",\"obj\":\"GO:0065007\",\"pred\":\"is_a\"},{\"sub\":\"GO:0019222\",\"obj\":\"GO:0065007\",\"pred\":\"is_a\"},{\"sub\":\"GO:0033554\",\"obj\":\"GO:0051716\",\"pred\":\"is_a\"},{\"sub\":\"GO:0044763\",\"obj\":\"GO:0009987\",\"pred\":\"is_a\"},{\"sub\":\"GO:0043488\",\"obj\":\"GO:0043487\",\"pred\":\"is_a\"},{\"sub\":\"GO:0009987\",\"obj\":\"GO:0008150\",\"pred\":\"is_a\"},{\"sub\":\"GO:0051716\",\"obj\":\"GO:0044763\",\"pred\":\"is_a\"},{\"sub\":\"GO:0010610\",\"obj\":\"GO:0043488\",\"pred\":\"is_a\"},{\"sub\":\"GO:2000815\",\"obj\":\"GO:0010610\",\"pred\":\"is_a\"},{\"sub\":\"GO:0060255\",\"obj\":\"GO:0043170\",\"pred\":\"regulates\"}]}",

http://golr.berkeleybop.org/select?qt=standard&fl=*&version=2.2&wt=json&indent=on&rows=1&q=id:%22GO:0044764%22&fq=document_category:%22ontology_class%22
"regulates_transitivity_graph_json":"{\"nodes\":[{\"id\":\"GO:0051704\",\"lbl\":\"multi-organism process\"},{\"id\":\"GO:0044764\",\"lbl\":\"multi-organism cellular process\"},{\"id\":\"GO:0009987\",\"lbl\":\"cellular process\"},{\"id\":\"GO:0008150\",\"lbl\":\"biological_process\"}],\"edges\":[{\"sub\":\"GO:0044764\",\"obj\":\"GO:0051704\",\"pred\":\"is_a\"},{\"sub\":\"GO:0044764\",\"obj\":\"GO:0009987\",\"pred\":\"is_a\"},{\"sub\":\"GO:0044764\",\"obj\":\"GO:0008150\",\"pred\":\"is_a\"}]}",
"topology_graph_json":"{\"nodes\":[{\"id\":\"GO:0016032\",\"lbl\":\"viral process\"},{\"id\":\"GO:0009292\",\"lbl\":\"genetic transfer\"},{\"id\":\"GO:0036281\",\"lbl\":\"coflocculation\"},{\"id\":\"GO:0051704\",\"lbl\":\"multi-organism process\"},{\"id\":\"GO:0042710\",\"lbl\":\"biofilm formation\"},{\"id\":\"GO:0044764\",\"lbl\":\"multi-organism cellular process\"},{\"id\":\"GO:0009987\",\"lbl\":\"cellular process\"},{\"id\":\"GO:0000128\",\"lbl\":\"flocculation\"},{\"id\":\"GO:0048874\",\"lbl\":\"homeostasis of number of cells in a free-living population\"},{\"id\":\"GO:0000746\",\"lbl\":\"conjugation\"},{\"id\":\"GO:0008150\",\"lbl\":\"biological_process\"}],\"edges\":[{\"sub\":\"GO:0044764\",\"obj\":\"GO:0051704\",\"pred\":\"is_a\"},{\"sub\":\"GO:0044764\",\"obj\":\"GO:0009987\",\"pred\":\"is_a\"},{\"sub\":\"GO:0000746\",\"obj\":\"GO:0044764\",\"pred\":\"is_a\"},{\"sub\":\"GO:0051704\",\"obj\":\"GO:0008150\",\"pred\":\"is_a\"},{\"sub\":\"GO:0009987\",\"obj\":\"GO:0008150\",\"pred\":\"is_a\"},{\"sub\":\"GO:0009292\",\"obj\":\"GO:0044764\",\"pred\":\"is_a\"},{\"sub\":\"GO:0016032\",\"obj\":\"GO:0044764\",\"pred\":\"is_a\"},{\"sub\":\"GO:0042710\",\"obj\":\"GO:0044764\",\"pred\":\"is_a\"},{\"sub\":\"GO:0000128\",\"obj\":\"GO:0044764\",\"pred\":\"is_a\"},{\"sub\":\"GO:0048874\",\"obj\":\"GO:0044764\",\"pred\":\"is_a\"},{\"sub\":\"GO:0036281\",\"obj\":\"GO:0044764\",\"pred\":\"is_a\"}]}",


regulates_transitivity_graph_json has only ancestors

"regulates_transitivity_graph_json":"{\"
{\"id\":\"GO:0016032\",\"lbl\":\"viral process\"},{\"id\":\"GO:0009292\",\"lbl\":\"genetic transfer\"},{\"id\":\"GO:0036281\",\"lbl\":\"coflocculation\"},{\"id\":\"GO:0042710\",\"lbl\":\"biofilm formation\"},{\"id\":\"GO:0000128\",\"lbl\":\"flocculation\"},{\"id\":\"GO:0048874\",\"lbl\":\"homeostasis of number of cells in a free-living population\"},{\"id\":\"GO:0000746\",\"lbl\":\"conjugation\"}],\"

{\"sub\":\"GO:0044764\",\"obj\":\"GO:0008150\",\"pred\":\"is_a\"}]}",
{\"sub\":\"GO:0000746\",\"obj\":\"GO:0044764\",\"pred\":\"is_a\"},{\"sub\":\"GO:0051704\",\"obj\":\"GO:0008150\",\"pred\":\"is_a\"},{\"sub\":\"GO:0009987\",\"obj\":\"GO:0008150\",\"pred\":\"is_a\"},{\"sub\":\"GO:0009292\",\"obj\":\"GO:0044764\",\"pred\":\"is_a\"},{\"sub\":\"GO:0016032\",\"obj\":\"GO:0044764\",\"pred\":\"is_a\"},{\"sub\":\"GO:0042710\",\"obj\":\"GO:0044764\",\"pred\":\"is_a\"},{\"sub\":\"GO:0000128\",\"obj\":\"GO:0044764\",\"pred\":\"is_a\"},{\"sub\":\"GO:0048874\",\"obj\":\"GO:0044764\",\"pred\":\"is_a\"},{\"sub\":\"GO:0036281\",\"obj\":\"GO:0044764\",\"pred\":\"is_a\"}]}",


"topology_graph_json":"{\"
nodes\":[{\"id\":\"GO:0016032\",\"lbl\":\"viral process\"},{\"id\":\"GO:0009292\",\"lbl\":\"genetic transfer\"},{\"id\":\"GO:0036281\",\"lbl\":\"coflocculation\"},{\"id\":\"GO:0051704\",\"lbl\":\"multi-organism process\"},{\"id\":\"GO:0042710\",\"lbl\":\"biofilm formation\"},{\"id\":\"GO:0044764\",\"lbl\":\"multi-organism cellular process\"},{\"id\":\"GO:0009987\",\"lbl\":\"cellular process\"},{\"id\":\"GO:0000128\",\"lbl\":\"flocculation\"},{\"id\":\"GO:0048874\",\"lbl\":\"homeostasis of number of cells in a free-living population\"},{\"id\":\"GO:0000746\",\"lbl\":\"conjugation\"},{\"id\":\"GO:0008150\",\"lbl\":\"biological_process\"}],\"
edges\":[{\"sub\":\"GO:0044764\",\"obj\":\"GO:0051704\",\"pred\":\"is_a\"},{\"sub\":\"GO:0044764\",\"obj\":\"GO:0009987\",\"pred\":\"is_a\"},{\"sub\":\"GO:0000746\",\"obj\":\"GO:0044764\",\"pred\":\"is_a\"},{\"sub\":\"GO:0051704\",\"obj\":\"GO:0008150\",\"pred\":\"is_a\"},{\"sub\":\"GO:0009987\",\"obj\":\"GO:0008150\",\"pred\":\"is_a\"},{\"sub\":\"GO:0009292\",\"obj\":\"GO:0044764\",\"pred\":\"is_a\"},{\"sub\":\"GO:0016032\",\"obj\":\"GO:0044764\",\"pred\":\"is_a\"},{\"sub\":\"GO:0042710\",\"obj\":\"GO:0044764\",\"pred\":\"is_a\"},{\"sub\":\"GO:0000128\",\"obj\":\"GO:0044764\",\"pred\":\"is_a\"},{\"sub\":\"GO:0048874\",\"obj\":\"GO:0044764\",\"pred\":\"is_a\"},{\"sub\":\"GO:0036281\",\"obj\":\"GO:0044764\",\"pred\":\"is_a\"}]}",




80135
{\"id\":\"GO:0000167\",\"lbl\":\"activation of MAPKKK activity involved in osmosensory signaling pathway\"},
{\"id\":\"GO:0000168\",\"lbl\":\"activation of MAPKK activity involved in osmosensory signaling pathway\"},
{\"id\":\"GO:0000169\",\"lbl\":\"activation of MAPK activity involved in osmosensory signaling pathway\"},
{\"id\":\"GO:0000173\",\"lbl\":\"inactivation of MAPK activity involved in osmosensory signaling pathway\"},
{\"id\":\"GO:0010363\",\"lbl\":\"regulation of plant-type hypersensitive response\"}],\"
{\"id\":\"GO:0010504\",\"lbl\":\"regulation of cell cycle arrest in response to nitrogen starvation\"},
{\"id\":\"GO:0010516\",\"lbl\":\"negative regulation of cellular response to nitrogen starvation\"},
{\"id\":\"GO:0010999\",\"lbl\":\"regulation of eIF2 alpha phosphorylation by heme\"},
{\"id\":\"GO:0016241\",\"lbl\":\"regulation of macroautophagy\"},
{\"id\":\"GO:0060733\",\"lbl\":\"regulation of eIF2 alpha phosphorylation by amino acid starvation\"},
{\"id\":\"GO:0060734\",\"lbl\":\"regulation of eIF2 alpha phosphorylation by endoplasmic reticulum stress\"},
{\"id\":\"GO:0060735\",\"lbl\":\"regulation of eIF2 alpha phosphorylation by dsRNA\"},
{\"id\":\"GO:0060905\",\"lbl\":\"regulation of induction of conjugation upon nitrogen starvation\"},
{\"id\":\"GO:0070302\",\"lbl\":\"regulation of stress-activated protein kinase signaling cascade\"},
{\"id\":\"GO:0070570\",\"lbl\":\"regulation of neuron projection regeneration\"},
{\"id\":\"GO:0080040\",\"lbl\":\"positive regulation of cellular response to phosphate starvation\"},
{\"id\":\"GO:0080136\",\"lbl\":\"priming of cellular response to stress\"},
{\"id\":\"GO:1900034\",\"lbl\":\"regulation of cellular response to heat\"},
{\"id\":\"GO:1900037\",\"lbl\":\"regulation of cellular response to hypoxia\"},
{\"id\":\"GO:1900069\",\"lbl\":\"regulation of cellular hyperosmotic salinity response\"},
{\"id\":\"GO:1900101\",\"lbl\":\"regulation of endoplasmic reticulum unfolded protein response\"},
{\"id\":\"GO:1900407\",\"lbl\":\"regulation of cellular response to oxidative stress\"},
{\"id\":\"GO:1901643\",\"lbl\":\"regulation of tRNA methylation in response to nitrogen starvation\"},
{\"id\":\"GO:1901966\",\"lbl\":\"regulation of cellular response to iron ion starvation\"},
{\"id\":\"GO:1902235\",\"lbl\":\"regulation of intrinsic apoptotic signaling pathway in response to endoplasmic reticulum stress\"},
{\"id\":\"GO:2000638\",\"lbl\":\"regulation of SREBP signaling pathway\"},
{\"id\":\"GO:2000772\",\"lbl\":\"regulation of cellular senescence\"},
{\"id\":\"GO:2001020\",\"lbl\":\"regulation of response to DNA damage stimulus\"},


edges\":[{\"sub\":\"GO:0080136\",\"obj\":\"GO:0080135\",\"pred\":\"is_a\"},{\"sub\":\"GO:0080135\",\"obj\":\"GO:0065007\",\"pred\":\"is_a\"},{\"sub\":\"GO:0033554\",\"obj\":\"GO:0006950\",\"pred\":\"is_a\"},{\"sub\":\"GO:0080134\",\"obj\":\"GO:0065007\",\"pred\":\"is_a\"},{\"sub\":\"GO:0080135\",\"obj\":\"GO:0080134\",\"pred\":\"is_a\"},{\"sub\":\"GO:0050794\",\"obj\":\"GO:0065007\",\"pred\":\"is_a\"},{\"sub\":\"GO:0010504\",\"obj\":\"GO:0080135\",\"pred\":\"is_a\"},{\"sub\":\"GO:0050789\",\"obj\":\"GO:0065007\",\"pred\":\"is_a\"},{\"sub\":\"GO:0050896\",\"obj\":\"GO:0008150\",\"pred\":\"is_a\"},{\"sub\":\"GO:0080040\",\"obj\":\"GO:0080135\",\"pred\":\"is_a\"},{\"sub\":\"GO:0080134\",\"obj\":\"GO:0006950\",\"pred\":\"regulates\"},{\"sub\":\"GO:0044763\",\"obj\":\"GO:0044699\",\"pred\":\"is_a\"},{\"sub\":\"GO:1901643\",\"obj\":\"GO:0080135\",\"pred\":\"is_a\"},{\"sub\":\"GO:0060905\",\"obj\":\"GO:0080135\",\"pred\":\"is_a\"},{\"sub\":\"GO:1901966\",\"obj\":\"GO:0080135\",\"pred\":\"is_a\"},{\"sub\":\"GO:0010363\",\"obj\":\"GO:0080135\",\"pred\":\"is_a\"},{\"sub\":\"GO:0010516\",\"obj\":\"GO:0080135\",\"pred\":\"is_a\"},{\"sub\":\"GO:0070302\",\"obj\":\"GO:0080135\",\"pred\":\"is_a\"},{\"sub\":\"GO:0044763\",\"obj\":\"GO:0009987\",\"pred\":\"is_a\"},{\"sub\":\"GO:0000169\",\"obj\":\"GO:0080135\",\"pred\":\"is_a\"},{\"sub\":\"GO:0080135\",\"obj\":\"GO:0033554\",\"pred\":\"regulates\"},{\"sub\":\"GO:0000168\",\"obj\":\"GO:0080135\",\"pred\":\"is_a\"},{\"sub\":\"GO:0048583\",\"obj\":\"GO:0065007\",\"pred\":\"is_a\"},{\"sub\":\"GO:0000167\",\"obj\":\"GO:0080135\",\"pred\":\"is_a\"},{\"sub\":\"GO:0051716\",\"obj\":\"GO:0044763\",\"pred\":\"is_a\"},{\"sub\":\"GO:1900407\",\"obj\":\"GO:0080135\",\"pred\":\"is_a\"},{\"sub\":\"GO:0048583\",\"obj\":\"GO:0050789\",\"pred\":\"is_a\"},{\"sub\":\"GO:1900101\",\"obj\":\"GO:0080135\",\"pred\":\"is_a\"},{\"sub\":\"GO:0006950\",\"obj\":\"GO:0050896\",\"pred\":\"is_a\"},{\"sub\":\"GO:0051716\",\"obj\":\"GO:0050896\",\"pred\":\"is_a\"},{\"sub\":\"GO:0048583\",\"obj\":\"GO:0050896\",\"pred\":\"regulates\"},{\"sub\":\"GO:0000173\",\"obj\":\"GO:0080135\",\"pred\":\"is_a\"},{\"sub\":\"GO:1902235\",\"obj\":\"GO:0080135\",\"pred\":\"is_a\"},{\"sub\":\"GO:0050794\",\"obj\":\"GO:0050789\",\"pred\":\"is_a\"},{\"sub\":\"GO:0010999\",\"obj\":\"GO:0080135\",\"pred\":\"is_a\"},{\"sub\":\"GO:0050794\",\"obj\":\"GO:0009987\",\"pred\":\"regulates\"},{\"sub\":\"GO:2000638\",\"obj\":\"GO:0080135\",\"pred\":\"is_a\"},{\"sub\":\"GO:0050789\",\"obj\":\"GO:0008150\",\"pred\":\"regulates\"},{\"sub\":\"GO:0080134\",\"obj\":\"GO:0048583\",\"pred\":\"is_a\"},{\"sub\":\"GO:2000772\",\"obj\":\"GO:0080135\",\"pred\":\"is_a\"},{\"sub\":\"GO:0065007\",\"obj\":\"GO:0008150\",\"pred\":\"is_a\"},{\"sub\":\"GO:1900034\",\"obj\":\"GO:0080135\",\"pred\":\"is_a\"},{\"sub\":\"GO:0080135\",\"obj\":\"GO:0050794\",\"pred\":\"is_a\"},{\"sub\":\"GO:0044699\",\"obj\":\"GO:0008150\",\"pred\":\"is_a\"},{\"sub\":\"GO:1900037\",\"obj\":\"GO:0080135\",\"pred\":\"is_a\"},{\"sub\":\"GO:2001020\",\"obj\":\"GO:0080135\",\"pred\":\"is_a\"},{\"sub\":\"GO:0060734\",\"obj\":\"GO:0080135\",\"pred\":\"is_a\"},{\"sub\":\"GO:0033554\",\"obj\":\"GO:0051716\",\"pred\":\"is_a\"},{\"sub\":\"GO:0060735\",\"obj\":\"GO:0080135\",\"pred\":\"is_a\"},{\"sub\":\"GO:1900069\",\"obj\":\"GO:0080135\",\"pred\":\"is_a\"},{\"sub\":\"GO:0009987\",\"obj\":\"GO:0008150\",\"pred\":\"is_a\"},{\"sub\":\"GO:0070570\",\"obj\":\"GO:0080135\",\"pred\":\"is_a\"},{\"sub\":\"GO:0016241\",\"obj\":\"GO:0080135\",\"pred\":\"is_a\"},{\"sub\":\"GO:0060733\",\"obj\":\"GO:0080135\",\"pred\":\"is_a\"}]}",
edges\":[{\"sub\":\"GO:0080135\",\"obj\":\"GO:0009987\",\"pred\":\"is_a\"},{\"sub\":\"GO:0080135\",\"obj\":\"GO:0050896\",\"pred\":\"regulates\"},{\"sub\":\"GO:0080135\",\"obj\":\"GO:0065007\",\"pred\":\"is_a\"},{\"sub\":\"GO:0080135\",\"obj\":\"GO:0033554\",\"pred\":\"is_a\"},{\"sub\":\"GO:0080135\",\"obj\":\"GO:0080134\",\"pred\":\"is_a\"},{\"sub\":\"GO:0080135\",\"obj\":\"GO:0050794\",\"pred\":\"is_a\"},{\"sub\":\"GO:0080135\",\"obj\":\"GO:0008150\",\"pred\":\"regulates\"},{\"sub\":\"GO:0080135\",\"obj\":\"GO:0050896\",\"pred\":\"is_a\"},{\"sub\":\"GO:0080135\",\"obj\":\"GO:0050789\",\"pred\":\"is_a\"},{\"sub\":\"GO:0080135\",\"obj\":\"GO:0009987\",\"pred\":\"regulates\"},{\"sub\":\"GO:0080135\",\"obj\":\"GO:0033554\",\"pred\":\"regulates\"},{\"sub\":\"GO:0080135\",\"obj\":\"GO:0006950\",\"pred\":\"is_a\"},{\"sub\":\"GO:0080135\",\"obj\":\"GO:0008150\",\"pred\":\"is_a\"},{\"sub\":\"GO:0080135\",\"obj\":\"GO:0044763\",\"pred\":\"regulates\"},{\"sub\":\"GO:0080135\",\"obj\":\"GO:0006950\",\"pred\":\"regulates\"},{\"sub\":\"GO:0080135\",\"obj\":\"GO:0048583\",\"pred\":\"is_a\"},{\"sub\":\"GO:0080135\",\"obj\":\"GO:0051716\",\"pred\":\"regulates\"},{\"sub\":\"GO:0080135\",\"obj\":\"GO:0044699\",\"pred\":\"regulates\"}]}",
