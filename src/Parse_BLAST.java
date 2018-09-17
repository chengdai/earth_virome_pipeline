
import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.File;
import java.io.FileReader;
import java.io.FileWriter;
import java.io.IOException;
import java.util.ArrayList;
import java.util.Hashtable;

/**
 *
 * @author gapavlop
 */
class Hit {

    public String source = "";
    public ArrayList<String> ID_hits = new ArrayList();
    public Hashtable<String, Integer> give_node_get_length = new Hashtable();

    public Hit() {
    }

    public void addIDs(String dest, Integer num) {
        if (!ID_hits.contains(dest)) {
            ID_hits.add(dest);
            give_node_get_length.put(dest, 0);
        }
        give_node_get_length.put(dest, Math.max(give_node_get_length.get(dest), num));
    }

}

public class Parse_BLAST {

    /**
     * @param args the command line arguments
     */
    static double similarity = 90;
    static double percent_length = 0.75;
    static double at_least_one_has_length = 1000;

    public static void main(String[] args) {
        Hashtable<String, Hit> give_name_get_Hit = new Hashtable();
        String filename = args[0];
        ArrayList<String> nodes = new ArrayList();

        int counter = 0;
        try {
            FileReader fileReader = new FileReader(filename);
            BufferedReader bufferedReader = new BufferedReader(fileReader);
            String line;
            while ((line = (bufferedReader.readLine())) != null) {
                line = filter(line);
                if (line.length() > 1) {
                    //System.out.println(line);
                    String[] str = line.split("\t");
                    int length = (int) (Math.abs(Double.parseDouble(str[3]) - Double.parseDouble(str[5])));
                    if (give_name_get_Hit.get(str[0]) == null) {
                        Hit h = new Hit();
                        if (!nodes.contains(str[0])) {
                            nodes.add(str[0]);
                        }
                        h.source = str[0];
                        h.addIDs(str[1], length);
                        give_name_get_Hit.put(str[0], h);
                    } else {
                        Hit h = give_name_get_Hit.get(str[0]);
                        h.addIDs(str[1], length);
                    }
                }
            }
            fileReader.close();
        } catch (Exception e) {
        }

        int ccc=0;
        for (int i = 0; i < nodes.size(); i++) {
            Hit h = give_name_get_Hit.get(nodes.get(i));
            
            for (int k = 0; k < h.ID_hits.size(); k++) {
                if(h.give_node_get_length.get(h.ID_hits.get(k))>=at_least_one_has_length){
                System.out.println(nodes.get(i)+"\t"+h.ID_hits.get(k)  );
                ccc++;       
                }
            }

        }
//System.out.println(ccc);
    }

    static String filter(String line) {
        // awk '{ if($1!~/^#/ && $3>=30) { if($13<=$14) { if(($4-$6)/($13+1) >=0.5) print ($1)} else { if(($4-$6)/($14+1) >=0.5) print ($1) } } }' | uniq | perl -p -i -e 's/\t /\t/g' 
        String str[] = line.split("\t");
        // System.out.println(Double.parseDouble(str[2]));
        if (Double.parseDouble(str[2]) >= similarity) {
            if (Double.parseDouble(str[12]) <= Double.parseDouble(str[13])) {
                if (Math.abs(Double.parseDouble(str[3]) - Double.parseDouble(str[5])) / (Double.parseDouble(str[12])) >= percent_length) {
                    return line;
                }
            } else if (Math.abs(Double.parseDouble(str[3]) - Double.parseDouble(str[5])) / (Double.parseDouble(str[13])) >= percent_length) {
                return line;
            }
        }
        return "";
    }


}
