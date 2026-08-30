package com.systema.modernized;

import java.util.HashMap;
import java.util.Map;

public class CicsTransactionContext {
    private static final ThreadLocal<Map<String, Object>> session = ThreadLocal.withInitial(HashMap::new);
    private static final ThreadLocal<Map<String, Map<String, Object>>> lastSendOptions = ThreadLocal.withInitial(HashMap::new);
    private static final ThreadLocal<Map<String, Map<String, Object>>> lastReceiveOptions = ThreadLocal.withInitial(HashMap::new);
    
    private static final Map<String, Map<String, String>> scriptedResponses = new HashMap<>();
    private static final Map<String, String> eibValues = new HashMap<>();

    public static void addScriptedResponse(String trigger, Map<String, String> response) {
        scriptedResponses.put(trigger.toUpperCase(), response);
    }

    public static void setEibValue(String name, String value) {
        eibValues.put(name.toUpperCase(), value);
    }
    
    public static void send(String map, String mapset, Object data) {
        send(map, mapset, data, new HashMap<>());
    }
    public static void send(String map, String mapset, Object data, Map<String, Object> options) {
        System.out.println("CICS SEND MAP: " + map + " MAPSET: " + mapset + " DATA: " + data + " OPTIONS: " + options);
        String key = mapset.toUpperCase() + "_" + map.toUpperCase();
        session.get().put(key + "_sent", data);
        lastSendOptions.get().put(key, options);
    }
    public static Object receive(String map, String mapset) {
        return receive(map, mapset, new HashMap<>());
    }
    public static Object receive(String map, String mapset, Map<String, Object> options) {
        System.out.println("CICS RECEIVE MAP: " + map + " MAPSET: " + mapset + " OPTIONS: " + options);
        String key = mapset.toUpperCase() + "_" + map.toUpperCase();
        lastReceiveOptions.get().put(key, options);
        
        String triggerKey = "SEND_MAP " + map.toUpperCase();
        if (scriptedResponses.containsKey(triggerKey)) {
            Map<String, String> fields = scriptedResponses.get(triggerKey);
            if (!fields.isEmpty()) {
                return fields.values().iterator().next();
            }
        }
        
        return session.get().get(key + "_input");
    }
    public static void setSessionInput(String map, String mapset, Object data) {
        session.get().put(mapset.toUpperCase() + "_" + map.toUpperCase() + "_input", data);
    }
    public static Object getSessionSent(String map, String mapset) {
        return session.get().get(mapset.toUpperCase() + "_" + map.toUpperCase() + "_sent");
    }
    public static Object getSendOption(String map, String mapset, String optionName) {
        Map<String, Object> opts = lastSendOptions.get().get(mapset.toUpperCase() + "_" + map.toUpperCase());
        return opts != null ? opts.get(optionName.toLowerCase()) : null;
    }
    public static Object getReceiveOption(String map, String mapset, String optionName) {
        Map<String, Object> opts = lastReceiveOptions.get().get(mapset.toUpperCase() + "_" + map.toUpperCase());
        return opts != null ? opts.get(optionName.toLowerCase()) : null;
    }
    public static String getEib(String fieldName) {
        return eibValues.getOrDefault(fieldName.toUpperCase(), "");
    }
    public static void cicsReturn() {
        System.out.println("CICS RETURN");
    }
    public static void clear() {
        session.get().clear();
        lastSendOptions.get().clear();
        lastReceiveOptions.get().clear();
    }
}
