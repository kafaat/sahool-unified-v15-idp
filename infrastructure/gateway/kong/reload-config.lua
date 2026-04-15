local http = require("resty.http")
local cjson = require("cjson")

local c = http.new()
local f = io.open("/kong/declarative/kong.yml", "r")
if not f then
  print("ERR: cannot open /kong/declarative/kong.yml")
  os.exit(1)
end
local body = f:read("*a")
f:close()

local payload = string.format('{"config": %s}', cjson.encode(body))
local res, err = c:request_uri("http://127.0.0.1:8001/config", {
  method  = "POST",
  headers = { ["Content-Type"] = "application/json" },
  body    = payload,
})

if res then
  print(res.status)
else
  print("ERR " .. tostring(err))
end
