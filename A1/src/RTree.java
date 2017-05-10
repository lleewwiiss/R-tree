import java.io.BufferedReader;
import java.io.FileReader;
import java.io.IOException;
import java.util.LinkedList;

public final class RTree<T> {
    private Node root;

    public RTree() {
        root = createRoot();
    }

    private Node createRoot() {
        float[] initCoordinates = new float[2];
        initCoordinates[0] = (float) Math.sqrt(Float.MAX_VALUE);
        initCoordinates[1] = (float) Math.sqrt(Float.MAX_VALUE);

        return new Node(true, initCoordinates);
    }

    public void insert(final float[] coordinates, final T entry) {
        Node.Entry e = new Node.Entry<>(coordinates, entry);


    }


    private static void loadPoints(String filename) {
        BufferedReader br = null;
        FileReader fr = null;
        try {
            fr = new FileReader(filename);
            br = new BufferedReader(fr);
            String sCurrentLine;
            while ((sCurrentLine = br.readLine()) != null) {
                System.out.println(sCurrentLine);
            }

        } catch (IOException e) {
            e.printStackTrace();
        } finally {
            try {
                if (br != null)
                    br.close();
                if (fr != null)
                    fr.close();
            } catch (IOException ex) {
                ex.printStackTrace();
            }
        }
    }

    private static class Node {
        Node parent;
        final boolean leaf;
        final LinkedList<Node> children;
        final float[] boundingBox;

        private Node(boolean leaf, float[] coordinates) {
            this.boundingBox = new float[coordinates.length];
            System.arraycopy(coordinates, 0, this.boundingBox, 0, coordinates.length);
            this.leaf = leaf;
            this.children = new LinkedList<>();
        }

        private static class Entry<T> extends Node {
            final T entry;

            Entry(final float[] coordinates, final T entry) {
                super(true, coordinates);
                this.entry = entry;
            }
        }
    }

    public static void main(String[] args) {
        loadPoints(args[0]);
    }
}

