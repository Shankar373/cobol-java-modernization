package com.systema.modernized.domain;

import java.math.BigDecimal;

public class Customer {

    private String customerId;
    private String name;
    private String status;
    private String city;
    private String state;
    private String riskLevel;
    private String reserved;

    public String getCustomerId() { return customerId; }
    public void setCustomerId(String val) { this.customerId = val; }

    public String getName() { return name; }
    public void setName(String val) { this.name = val; }

    public String getStatus() { return status; }
    public void setStatus(String val) { this.status = val; }

    public String getCity() { return city; }
    public void setCity(String val) { this.city = val; }

    public String getState() { return state; }
    public void setState(String val) { this.state = val; }

    public String getRiskLevel() { return riskLevel; }
    public void setRiskLevel(String val) { this.riskLevel = val; }

    public String getReserved() { return reserved; }
    public void setReserved(String val) { this.reserved = val; }

}