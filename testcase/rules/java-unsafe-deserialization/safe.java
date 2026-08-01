import java.io.DataInputStream;
import java.io.IOException;
import java.io.InputStream;

class SafeDeserializationExample {
    String readTextValue(InputStream source) throws IOException {
        DataInputStream input = new DataInputStream(source);
        return input.readUTF();
    }
}

