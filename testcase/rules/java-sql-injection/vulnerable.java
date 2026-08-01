import java.sql.Connection;
import java.sql.SQLException;
import java.sql.Statement;

class UnsafeSqlExample {
    void executeQueries(Connection connection, String userId) throws SQLException {
        Statement statement = connection.createStatement();

        statement.executeQuery("SELECT * FROM users WHERE id = '" + userId + "'");
        statement.execute("DELETE FROM sessions WHERE user_id = '" + userId + "'");
        statement.executeUpdate("UPDATE users SET active = 1 WHERE id = '" + userId + "'");
    }
}

