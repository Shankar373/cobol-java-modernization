package com.systema.modernized;
import java.util.HashMap;
import java.util.Map;
public class JclExecutionContext {
    private static final ThreadLocal<Map<String, String>> ddAssignments = ThreadLocal.withInitial(HashMap::new);
    private static final ThreadLocal<Map<String, String>> sysinData = ThreadLocal.withInitial(HashMap::new);
    private static final ThreadLocal<Map<String, Integer>> stepReturnCodes = ThreadLocal.withInitial(HashMap::new);
    
    public static void setDdAssignment(String ddName, String physicalPath) {
        ddAssignments.get().put(ddName.toUpperCase(), physicalPath);
    }
    
    public static String getDdAssignment(String ddName) {
        return ddAssignments.get().get(ddName.toUpperCase());
    }
    
    public static void setSysinData(String ddName, String data) {
        sysinData.get().put(ddName.toUpperCase(), data);
    }
    
    public static String getSysinData(String ddName) {
        return sysinData.get().get(ddName.toUpperCase());
    }
    
    public static void setStepReturnCode(String stepName, int rc) {
        stepReturnCodes.get().put(stepName.toUpperCase(), rc);
    }
    
    public static Integer getStepReturnCode(String stepName) {
        return stepReturnCodes.get().getOrDefault(stepName.toUpperCase(), 0);
    }
    
    public static boolean checkAnyStepCond(int code, String op) {
        for (int rc : stepReturnCodes.get().values()) {
            if (compareRc(code, op, rc)) {
                return true;
            }
        }
        return false;
    }
    
    public static boolean compareRc(int code, String op, int rc) {
        switch (op.toUpperCase()) {
            case "EQ": return code == rc;
            case "NE": return code != rc;
            case "GT": return code > rc;
            case "LT": return code < rc;
            case "GE": return code >= rc;
            case "LE": return code <= rc;
            default: return false;
        }
    }
    
    public static void clear() {
        ddAssignments.get().clear();
        sysinData.get().clear();
        stepReturnCodes.get().clear();
    }
}
