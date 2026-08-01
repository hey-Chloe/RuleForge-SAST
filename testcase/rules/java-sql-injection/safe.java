import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;

class SafeSqlExample {
    ResultSet findUser(Connection connection, String userId) throws SQLException {
        PreparedStatement statement = connection.prepareStatement(
            "SELECT * FROM users WHERE id = ?"
        );
        statement.setString(1, userId);
        return statement.executeQuery();
    }
}

