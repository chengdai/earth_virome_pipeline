#!/usr/bin/perl

my $filename_data = $ARGV[0];
my $filename_out = $ARGV[1];
my $full_connections = {};


open FILE, "<", $filename_data or die $!;

while (<FILE>){
    chomp;
    my $line = $_;
    my @elements = split ("\t", $line);
$full_connections->{$elements[0]}->{$elements[1]} = 1;
$full_connections->{$elements[1]}->{$elements[0]} = 1;
}


close (FILE);


my %all_graph = ();
my $current_graph = 0;
my %visited = ();
my @to_visit = ();
foreach my $node (keys %$full_connections) {
    next if exists $visited{$node};
    $current_graph++;
    @to_visit=($node);
    while (@to_visit) {
        $node_to_visit = shift @to_visit;
        $visited{$node_to_visit} = $current_graph;
        push @to_visit, grep { !exists $visited{$_} }
                              keys %{ $full_connections->{$node_to_visit} };
    }
}


my $max = 0;
$_ > $max and $max = $_ for values %visited;

open(my $fh, '>', $filename_out);


my $cluster_new=1;
for (my $i=1; $i <= $max; $i++) {
 print $fh "$i\t";
 $cluster_new=0;
 foreach $key (keys %visited)
 { 
  if($visited{$key}==$i && $cluster_new==1)
	{
  	 print $fh ",$key";
	}
  if($visited{$key}==$i && $cluster_new==0)
        {
         print $fh "$key";
	  $cluster_new=1;
        }
 }
print $fh "\n";
   
}


close $fh;

