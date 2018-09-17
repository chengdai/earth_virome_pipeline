
import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.File;
import java.io.FileReader;
import java.io.FileWriter;
import java.io.IOException;
import java.util.ArrayList;
import java.util.Collections;
import java.util.Comparator;
import java.util.Hashtable;

/**
 *
 * @author Georgios Pavlopoulos
 *
 */
class Interval {

    public int sum_histogram = 0;
    private int left;
    private int right;

    public Interval(int left, int right) {
        if (left <= right) {
            this.left = left;
            this.right = right;
        } else {
            this.left = right;
            this.right = left;
        }
    }

    public int getLeft() {
        return left;
    }

    public int getRight() {
        return right;
    }

    public int getLength() {
        return Math.abs(right - left) + 1;
    }

    // does this interval a intersect b?
    public boolean intersects(Interval b) {
        Interval a = this;
        if (b.left <= a.right && b.left >= a.left) {
            return true;
        }
        if (a.left <= b.right && a.left >= b.left) {
            return true;
        }
        return false;
    }

    public boolean intersects(int num) {
        Interval a = this;
        if (a.left <= num && a.right >= num) {
            return true;
        }

        return false;
    }

    public String toString() {
        return "[" + left + ", " + right + "]";
    }

}

class IntervalComparator implements Comparator<Interval> {

    public int compare(Interval i1, Interval i2) {
        return i1.getLeft() - i2.getLeft();
    }
}

class Virus {

    public String name = "";
    public ArrayList<Interval> intervals = new ArrayList();
    public int metagenome_length = 0;
    public double coverage = 0;

    public void Virus() {

    }

}

public class Coverage_VIRUSES_10Percent {

    /**
     * @param args the command line arguments
     */
    static Hashtable<String, Virus> give_name_get_virus = new Hashtable();
    static ArrayList<String> virus_names = new ArrayList();
    static Hashtable<String, Integer> virus_names_passing_the_filter = new Hashtable();

    public static void main(String[] args) {
        System.out.println("Compile like: javac Coverage_VIRUSES_10Percent.java \nRun like: java Coverage_VIRUSES_10Percent blasttabfile.\nResults will be automatically saved in a .10percent.txt file");

        String filename = "/Users/gapavlop/Desktop/3300001348_u_vs_mVCs.blout";
        filename = args[0];
        String output_file = filename + ".10percent.txt";
        long lines_cnt = 0;
        try {

            FileReader fileReader = new FileReader(filename);
            BufferedReader bufferedReader = new BufferedReader(fileReader);
            String line;
            while ((line = bufferedReader.readLine()) != null) {
                if (line.length() > 2) {
                    String[] sss = line.split("\t");
                    String virus = sss[1];
                    if (give_name_get_virus.get(virus) == null) {
                        Virus vv = new Virus();
                        Interval iii = new Interval(Integer.parseInt(sss[8]), Integer.parseInt(sss[9]));
                        vv.intervals.add(iii);
                        vv.name = virus;
                        vv.metagenome_length = Integer.parseInt(sss[13]);
                        give_name_get_virus.put(virus, vv);
                    } else {
                        Virus vv = give_name_get_virus.get(virus);
                        Interval iii = new Interval(Integer.parseInt(sss[8]), Integer.parseInt(sss[9]));
                        vv.intervals.add(iii);
                    }

                }
                if (lines_cnt % 100000 == 0) {
                    System.out.println("Loading " + lines_cnt + " lines");
                }
                lines_cnt++;
            }
            fileReader.close();
        } catch (Exception e) {
            e.printStackTrace();
        }
        System.out.println("Loaded " + lines_cnt + " lines");

        virus_names = Collections.list(give_name_get_virus.keys());
        System.out.println("Loaded " + virus_names.size() + " entities");

        for (int i = 0; i < virus_names.size(); i++) {
            if (i % 1000 == 0) {
                System.out.println("Filtering:" + i + "/" + virus_names.size());
            }
            Virus vvv = give_name_get_virus.get(virus_names.get(i));
            if (vvv != null) {
                vvv.coverage = coverage(vvv.intervals);
            }
        }
        System.out.println("finished coverage calculation");

      //  Virus v = give_name_get_virus.get("3300002488.a:JGI25128J35275_1001383");
      //  System.out.println(v.name);
      //  System.out.println(v.intervals);
      //  System.out.println(v.coverage);

        for (int i = 0; i < virus_names.size(); i++) {
            if (i % 10000 == 0) {
                System.out.println("Filtering:" + i + "/" + virus_names.size());
            }
            Virus vvv = give_name_get_virus.get(virus_names.get(i));
            if ((double) ((double) vvv.coverage * 100 / (double) vvv.metagenome_length) >= 10) {
                virus_names_passing_the_filter.put(virus_names.get(i), 1);
            }
        }

        StringBuffer buf = new StringBuffer();
        write_to_file(output_file, "");
        long counter = 0;
        try {
            FileReader fileReader = new FileReader(filename);
            BufferedReader bufferedReader = new BufferedReader(fileReader);
            String line;
            while ((line = bufferedReader.readLine()) != null) {
                if (line.length() > 2) {
                    String[] sss = line.split("\t");
                    if (virus_names_passing_the_filter.get(sss[1]) != null) {
                        buf.append(line + "\n");
                        if (counter % 100000 == 0) {
                            append_to_file(output_file, buf.toString());
                            buf.setLength(0);
                        }
                    }
                }
                if (counter % 1000 == 0) {
                    System.out.println("Storing results:" + counter + "/" + lines_cnt);
                }
                counter++;
            }
            append_to_file(output_file, buf.toString());
            buf.setLength(0);
            fileReader.close();
        } catch (Exception e) {

            e.printStackTrace();
        }

    }//main

    public static int coverage(ArrayList<Interval> intervals) {
        int coverage = 0;
        if (intervals.size() == 0) {
            return 0;
        }
        if (intervals.size() == 1) {
            Math.abs(intervals.get(0).getRight() - intervals.get(0).getLeft());
        }
        Collections.sort(intervals, new IntervalComparator());
        Interval first = intervals.get(0);
        int start = first.getLeft();
        int end = first.getRight();
        ArrayList<Interval> result = new ArrayList<Interval>();
        for (int i = 1; i < intervals.size(); i++) {
            Interval current = intervals.get(i);
            if (current.getLeft() <= end) {
                end = Math.max(current.getRight(), end);
            } else {
                result.add(new Interval(start, end));
                start = current.getLeft();
                end = current.getRight();
            }
        }
        result.add(new Interval(start, end));
        for (int i = 0; i < result.size(); i++) {
            coverage += Math.abs(result.get(i).getRight() - result.get(i).getLeft());
        }
        return coverage + result.size();
    }

    static void append_to_file(String filename, String message) {
        try {
            FileWriter fw = new FileWriter(filename, true); //the true will append the new data
            fw.write(message);//appends the string to the file
            fw.close();
        } catch (IOException ioe) {
            System.err.println("IOException: " + ioe.getMessage());
        }
    }

    static void write_to_file(String filename, String message) {
        BufferedWriter output = null;
        try {
            File file = new File(filename);
            output = new BufferedWriter(new FileWriter(file));
            output.write(message);
            output.close();
        } catch (IOException e) {
            e.printStackTrace();
        }
    }
}

