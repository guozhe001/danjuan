import pysnowball as ball

ball.set_token("")
flow = ball.quote_detail('SH600000')

print(flow)
