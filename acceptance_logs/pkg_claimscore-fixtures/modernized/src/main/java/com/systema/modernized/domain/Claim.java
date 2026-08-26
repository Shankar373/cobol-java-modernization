package com.systema.modernized.domain;

import java.math.BigDecimal;

public class Claim {

    private String id;
    private Integer date;
    private Integer time;
    private String policyId;
    private String type;
    private String channel;
    private BigDecimal lossAmount;
    private String description;
    private String reportedBy;
    private String reserved;

    public String getId() { return id; }
    public void setId(String val) { this.id = val; }

    public Integer getDate() { return date; }
    public void setDate(Integer val) { this.date = val; }

    public Integer getTime() { return time; }
    public void setTime(Integer val) { this.time = val; }

    public String getPolicyId() { return policyId; }
    public void setPolicyId(String val) { this.policyId = val; }

    public String getType() { return type; }
    public void setType(String val) { this.type = val; }

    public String getChannel() { return channel; }
    public void setChannel(String val) { this.channel = val; }

    public BigDecimal getLossAmount() { return lossAmount; }
    public void setLossAmount(BigDecimal val) { this.lossAmount = val; }

    public String getDescription() { return description; }
    public void setDescription(String val) { this.description = val; }

    public String getReportedBy() { return reportedBy; }
    public void setReportedBy(String val) { this.reportedBy = val; }

    public String getReserved() { return reserved; }
    public void setReserved(String val) { this.reserved = val; }

}