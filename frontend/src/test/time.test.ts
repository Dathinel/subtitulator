import { describe, expect, it } from "vitest";
import { formatTimecode, parseTimecode } from "../utils/time";

describe("formatTimecode", () => {
  it("formatea segundos a mm:ss.cc", () => {
    expect(formatTimecode(0)).toBe("00:00.00");
    expect(formatTimecode(75.5)).toBe("01:15.50");
    expect(formatTimecode(3.21)).toBe("00:03.21");
  });

  it("protege valores inválidos", () => {
    expect(formatTimecode(-5)).toBe("00:00.00");
    expect(formatTimecode(NaN)).toBe("00:00.00");
  });
});

describe("parseTimecode", () => {
  it("convierte timecodes válidos a segundos", () => {
    expect(parseTimecode("01:15.50")).toBeCloseTo(75.5, 2);
    expect(parseTimecode("00:03.21")).toBeCloseTo(3.21, 2);
    expect(parseTimecode("12.5")).toBeCloseTo(12.5, 2);
  });

  it("rechaza entradas inválidas", () => {
    expect(parseTimecode("")).toBeNull();
    expect(parseTimecode("abc")).toBeNull();
    expect(parseTimecode("00:99.00")).toBeNull();
  });

  it("es inverso de formatTimecode", () => {
    const seconds = 123.45;
    const parsed = parseTimecode(formatTimecode(seconds));
    expect(parsed).toBeCloseTo(seconds, 2);
  });
});
