import supertest from "supertest";
import api from "../src/api";

describe("GET /api/results/summary", () => {

  test("It should return 200 status code for successful results", async () => {
  	process.env.DATA_PATH = './tests/resources/results/without_failures';
    const response = await supertest(api).get("/api/results/summary");
    expect(response.statusCode).toBe(200);
  });

  test("It should return 500 status code for result failures", async () => {
  	process.env.DATA_PATH = './tests/resources/results/with_failures';
    const response = await supertest(api).get("/api/results/summary");
    expect(response.statusCode).toBe(500);
  });

});