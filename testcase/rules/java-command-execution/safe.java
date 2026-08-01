class SafeCommandExample {
    String selectAllowedAction(String requestedAction) {
        if ("status".equals(requestedAction)) {
            return "STATUS";
        }
        return "UNKNOWN";
    }
}

