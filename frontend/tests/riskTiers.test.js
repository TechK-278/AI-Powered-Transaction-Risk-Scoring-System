import assert from "node:assert/strict";
import { describe, it } from "node:test";

import { RISK_TIERS, findRiskTier, findRiskTierForScore } from "../src/domain/riskTiers.js";

describe("risk tiers", () => {
  it("cover every score from 0 to 100 exactly once", () => {
    for (let score = 0; score <= 100; score += 1) {
      const matchingTiers = RISK_TIERS.filter((tier) => score >= tier.minScore && score <= tier.maxScore);
      assert.equal(matchingTiers.length, 1, `score ${score}`);
    }
  });

  it("match the backend RiskScoreEngine boundaries (30 / 70)", () => {
    assert.equal(findRiskTierForScore(30).label, "Low");
    assert.equal(findRiskTierForScore(31).label, "Medium");
    assert.equal(findRiskTierForScore(70).label, "Medium");
    assert.equal(findRiskTierForScore(71).label, "High");
  });

  it("returns null for unknown labels", () => {
    assert.equal(findRiskTier("Critical"), null);
    assert.equal(findRiskTier("High").tone, "high");
  });
});
