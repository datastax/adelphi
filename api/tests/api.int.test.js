import supertest from "supertest";
import api from "../src/api";

describe("GET /api/results/summary", () => {

  test("It should return 200 status code for successful results", async () => {
  	process.env.DATA_PATH = './tests/resources/results/without_failures';
    const response = await supertest(api).get("/api/results/summary");
    expect(response.body.gemini.write_ops).toBe(22239);
    expect(response.body.gemini.write_errors).toBe(0);
    expect(response.body.gemini.read_ops).toBe(35);
    expect(response.body.gemini.read_errors).toBe(0);
    expect(response.body.cassandra_diff.matched_partitions).toBe(1000);
    expect(response.body.cassandra_diff.matched_rows).toBe(1000);
    expect(response.body.cassandra_diff.matched_values).toBe(2000);
    expect(response.body.cassandra_diff.mismatched_partitions).toBe(0);
    expect(response.body.cassandra_diff.partitions_only_in_source).toBe(0);
    expect(response.body.cassandra_diff.partitions_only_in_target).toBe(0);
    expect(response.statusCode).toBe(200);
  });

  test("It should return 500 status code for result failures", async () => {
  	process.env.DATA_PATH = './tests/resources/results/with_failures';
    const response = await supertest(api).get("/api/results/summary");
    expect(response.body.gemini.write_ops).toBe(22239);
    expect(response.body.gemini.write_errors).toBe(0);
    expect(response.body.gemini.read_ops).toBe(35);
    expect(response.body.gemini.read_errors).toBe(0);
    expect(response.body.cassandra_diff.matched_partitions).toBe(1000);
    expect(response.body.cassandra_diff.matched_rows).toBe(1000);
    expect(response.body.cassandra_diff.matched_values).toBe(2000);
    expect(response.body.cassandra_diff.mismatched_partitions).toBe(1000);
    expect(response.body.cassandra_diff.partitions_only_in_source).toBe(1000);
    expect(response.body.cassandra_diff.partitions_only_in_target).toBe(0);
    expect(response.statusCode).toBe(500);
  });

});