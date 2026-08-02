package testcase;

import org.w3c.dom.Document;
import org.xml.sax.InputSource;

import javax.naming.directory.DirContext;
import javax.naming.directory.InitialDirContext;
import javax.xml.parsers.DocumentBuilder;
import javax.xml.parsers.DocumentBuilderFactory;
import java.io.ByteArrayInputStream;
import java.io.File;
import java.io.FileInputStream;
import java.io.InputStream;
import java.io.ObjectInputStream;
import java.net.HttpURLConnection;
import java.net.URI;
import java.net.URL;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.security.MessageDigest;
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.Statement;
import java.util.Base64;
import java.util.Hashtable;
import java.util.Map;

public class VulnerableController {

    private static final String DATABASE_URL =
            "jdbc:mysql://127.0.0.1:3306/demo";

    private static final String DATABASE_USER = "root";

    private static final String DATABASE_PASSWORD =
            "root123456";

    private static final Path UPLOAD_DIRECTORY =
            Paths.get("C:/app/uploads").toAbsolutePath().normalize();

    public String findUser(String userId) throws Exception {
        String normalizedId = normalizeInput(userId);
        return queryUser(normalizedId);
    }

    private String normalizeInput(String value) {
        if (value == null) {
            return "";
        }

        return value.trim();
    }

    private String queryUser(String userId) throws Exception {
        Connection connection = DriverManager.getConnection(
                DATABASE_URL,
                DATABASE_USER,
                DATABASE_PASSWORD
        );

        Statement statement = connection.createStatement();

        String sql =
                "SELECT username, email FROM users "
                + "WHERE id = '" + userId + "'";

        ResultSet resultSet = statement.executeQuery(sql);

        if (resultSet.next()) {
            return resultSet.getString("username")
                    + ":"
                    + resultSet.getString("email");
        }

        return "not found";
    }

    public String findUserSafely(String userId) throws Exception {
        Connection connection = DriverManager.getConnection(
                DATABASE_URL,
                DATABASE_USER,
                DATABASE_PASSWORD
        );

        String sql =
                "SELECT username, email FROM users WHERE id = ?";

        PreparedStatement statement =
                connection.prepareStatement(sql);

        statement.setString(1, userId);

        ResultSet resultSet = statement.executeQuery();

        if (resultSet.next()) {
            return resultSet.getString("username");
        }

        return "not found";
    }

    public String executeDiagnostic(
            Map<String, String> parameters
    ) throws Exception {

        String host = parameters.get("host");
        String count = parameters.getOrDefault("count", "1");

        String command = buildPingCommand(host, count);

        Process process = new ProcessBuilder(
                "cmd.exe",
                "/c",
                command
        ).start();

        byte[] output = process.getInputStream().readAllBytes();

        return new String(
                output,
                StandardCharsets.UTF_8
        );
    }

    private String buildPingCommand(
            String host,
            String count
    ) {
        return "ping -n "
                + count
                + " "
                + host;
    }

    public byte[] downloadFile(String requestedFile)
            throws Exception {

        String decodedName =
                URLDecoderHelper.decode(requestedFile);

        Path targetPath = UPLOAD_DIRECTORY.resolve(
                decodedName
        ).normalize();

        return Files.readAllBytes(targetPath);
    }

    public byte[] downloadFileSafely(String requestedFile)
            throws Exception {

        Path targetPath = UPLOAD_DIRECTORY.resolve(
                requestedFile
        ).normalize();

        if (!targetPath.startsWith(UPLOAD_DIRECTORY)) {
            throw new SecurityException(
                    "Invalid file path"
            );
        }

        return Files.readAllBytes(targetPath);
    }

    public Object restoreSession(String encodedData)
            throws Exception {

        byte[] serializedData =
                Base64.getDecoder().decode(encodedData);

        InputStream inputStream =
                new ByteArrayInputStream(serializedData);

        ObjectInputStream objectInputStream =
                new ObjectInputStream(inputStream);

        return objectInputStream.readObject();
    }

    public String parseXml(String xmlContent)
            throws Exception {

        DocumentBuilderFactory factory =
                DocumentBuilderFactory.newInstance();

        factory.setNamespaceAware(true);

        DocumentBuilder builder =
                factory.newDocumentBuilder();

        Document document = builder.parse(
                new InputSource(
                        new ByteArrayInputStream(
                                xmlContent.getBytes(
                                        StandardCharsets.UTF_8
                                )
                        )
                )
        );

        return document
                .getDocumentElement()
                .getTextContent();
    }

    public String fetchRemoteResource(String targetUrl)
            throws Exception {

        URI uri = URI.create(targetUrl);
        URL url = uri.toURL();

        HttpURLConnection connection =
                (HttpURLConnection) url.openConnection();

        connection.setConnectTimeout(5000);
        connection.setReadTimeout(5000);

        try (InputStream inputStream =
                     connection.getInputStream()) {

            return new String(
                    inputStream.readAllBytes(),
                    StandardCharsets.UTF_8
            );
        }
    }

    public Object searchEmployee(String username)
            throws Exception {

        Hashtable<String, String> environment =
                new Hashtable<>();

        environment.put(
                "java.naming.factory.initial",
                "com.sun.jndi.ldap.LdapCtxFactory"
        );

        environment.put(
                "java.naming.provider.url",
                "ldap://127.0.0.1:389"
        );

        DirContext context =
                new InitialDirContext(environment);

        String filter =
                "(&(objectClass=person)(uid="
                + username
                + "))";

        return context.search(
                "ou=users,dc=example,dc=com",
                filter,
                null
        );
    }

    public String calculatePasswordHash(String password)
            throws Exception {

        MessageDigest digest =
                MessageDigest.getInstance("MD5");

        byte[] hash = digest.digest(
                password.getBytes(
                        StandardCharsets.UTF_8
                )
        );

        return Base64.getEncoder()
                .encodeToString(hash);
    }

    public String loadTemplate(String templatePath)
            throws Exception {

        File templateFile = new File(templatePath);

        try (FileInputStream inputStream =
                     new FileInputStream(templateFile)) {

            return new String(
                    inputStream.readAllBytes(),
                    StandardCharsets.UTF_8
            );
        }
    }

    private static final class URLDecoderHelper {

        private URLDecoderHelper() {
        }

        static String decode(String value) {
            return java.net.URLDecoder.decode(
                    value,
                    StandardCharsets.UTF_8
            );
        }
    }
}