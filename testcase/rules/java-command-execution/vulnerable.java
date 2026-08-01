import java.io.IOException;

class UnsafeCommandExample {
    Process executeUserCommand(String command) throws IOException {
        return Runtime.getRuntime().exec(command);
    }
}

