/**
 * Unit tests for the FieldView-compatible error envelope filter.
 * Ensures the wire shape matches `{error: {code, id, message, path?}}`
 * except on /oauth/token and /oauth/revoke where we pass through the
 * raw OAuth 2.0 body (RFC 6749 § 5.2 / RFC 7009 § 2.2.1).
 */

import {
  BadRequestException,
  InternalServerErrorException,
  UnauthorizedException,
} from "@nestjs/common";
import type { ArgumentsHost } from "@nestjs/common";
import { PartnerErrorFilter } from "../utils/partner-error.filter";

type Spy = jest.Mock;

function makeHost(path: string): {
  host: ArgumentsHost;
  resStatus: Spy;
  resJson: Spy;
  resSetHeader: Spy;
} {
  const resStatus: Spy = jest.fn().mockReturnThis();
  const resJson: Spy = jest.fn();
  const resSetHeader: Spy = jest.fn();
  const res = { status: resStatus, json: resJson, setHeader: resSetHeader };
  const req = { path, headers: {} };
  const http = {
    getResponse: () => res,
    getRequest: () => req,
  };
  const host = { switchToHttp: () => http } as unknown as ArgumentsHost;
  return { host, resStatus, resJson, resSetHeader };
}

describe("PartnerErrorFilter", () => {
  const filter = new PartnerErrorFilter();

  it("wraps a generic HttpException in FieldView envelope", () => {
    const { host, resStatus, resJson } = makeHost("/partner/v1/fields");
    filter.catch(new UnauthorizedException("nope"), host);

    expect(resStatus).toHaveBeenCalledWith(401);
    const body = resJson.mock.calls[0][0];
    expect(body.error.code).toBe("invalid_client");
    expect(body.error.message).toBe("nope");
    expect(typeof body.error.id).toBe("string");
    expect(body.error.path).toBe("/partner/v1/fields");
  });

  it("maps 500 to server_error code", () => {
    const { host, resStatus, resJson } = makeHost("/partner/v1/anything");
    filter.catch(new InternalServerErrorException("boom"), host);
    expect(resStatus).toHaveBeenCalledWith(500);
    expect(resJson.mock.calls[0][0].error.code).toBe("server_error");
  });

  it("passes through raw OAuth error body on /oauth/token", () => {
    const { host, resStatus, resJson } = makeHost("/partner/v1/oauth/token");
    const exc = new BadRequestException({
      error: "invalid_grant",
      error_description: "Code expired",
    });
    filter.catch(exc, host);
    expect(resStatus).toHaveBeenCalledWith(400);
    const body = resJson.mock.calls[0][0];
    // RFC 6749 § 5.2 wire shape — not wrapped
    expect(body).toEqual({
      error: "invalid_grant",
      error_description: "Code expired",
    });
  });

  it("echoes X-Request-Id back in response header", () => {
    const { host, resSetHeader } = makeHost("/partner/v1/fields");
    filter.catch(new UnauthorizedException("nope"), host);
    expect(resSetHeader).toHaveBeenCalledWith(
      "X-Request-Id",
      expect.any(String),
    );
  });
});
