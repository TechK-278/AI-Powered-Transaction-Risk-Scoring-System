import assert from "node:assert/strict";
import { describe, it } from "node:test";

import {
  PCA_COMPONENT_KEYS,
  buildEvaluationPayload,
  createEmptyTransactionForm,
  parseDatasetRow,
  validateTransactionForm,
} from "../src/domain/transactionPayload.js";

function datasetRowValues({ time = 406, amount = 0.0, withClass = false } = {}) {
  const pcaValues = PCA_COMPONENT_KEYS.map((_, index) => (index % 2 === 0 ? -1.25 : 0.5));
  const cells = [time, ...pcaValues, amount];
  return (withClass ? [...cells, 1] : cells).join(",");
}

describe("validateTransactionForm", () => {
  it("rejects a blank or non-positive amount", () => {
    const form = createEmptyTransactionForm();
    assert.ok(validateTransactionForm(form).amount);
    assert.ok(validateTransactionForm({ ...form, amount: "0" }).amount);
    assert.ok(validateTransactionForm({ ...form, amount: "-3" }).amount);
  });

  it("rejects negative time and non-numeric PCA values", () => {
    const form = { ...createEmptyTransactionForm(), amount: "10", time: "-1", v7: "abc" };
    const fieldErrors = validateTransactionForm(form);
    assert.ok(fieldErrors.time);
    assert.ok(fieldErrors.v7);
  });

  it("accepts a complete valid form", () => {
    const form = { ...createEmptyTransactionForm(), amount: "149.50", time: "3600" };
    assert.deepEqual(validateTransactionForm(form), {});
  });
});

describe("buildEvaluationPayload", () => {
  it("converts form strings to numbers using backend field names", () => {
    const form = { ...createEmptyTransactionForm(), amount: "149.50", time: "3600", v14: "-2.5" };
    const payload = buildEvaluationPayload(form);
    assert.equal(payload.amount, 149.5);
    assert.equal(payload.time, 3600);
    assert.equal(payload.v14, -2.5);
    assert.equal(Object.keys(payload).length, 30);
  });
});

describe("parseDatasetRow", () => {
  it("maps Time, V1–V28 and Amount columns", () => {
    const formValues = parseDatasetRow(datasetRowValues({ time: 406, amount: 529 }));
    assert.equal(formValues.time, "406");
    assert.equal(formValues.v1, "-1.25");
    assert.equal(formValues.v2, "0.5");
    assert.equal(formValues.amount, "529");
  });

  it("ignores a trailing Class column and surrounding quotes", () => {
    const quotedRow = datasetRowValues({ amount: 12, withClass: true })
      .split(",")
      .map((cell) => `"${cell}"`)
      .join(",");
    const formValues = parseDatasetRow(quotedRow);
    assert.equal(formValues.amount, "12");
    assert.equal(formValues.Class, undefined);
  });

  it("reports the wrong number of values", () => {
    assert.throws(() => parseDatasetRow("1,2,3"), /Expected 30 values/);
  });

  it("reports the first non-numeric value", () => {
    const cells = datasetRowValues({ amount: 5 }).split(",");
    cells[3] = "n/a";
    assert.throws(() => parseDatasetRow(cells.join(",")), /Value 4 \("n\/a"\)/);
  });
});
