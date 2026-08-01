import java.io.IOException;
import java.io.InputStream;
import java.io.ObjectInputStream;

class UnsafeDeserializationExample {
    Object readUntrustedObject(InputStream source) throws IOException, ClassNotFoundException {
        ObjectInputStream objectInput = new ObjectInputStream(source);
        return objectInput.readObject();
    }
}

