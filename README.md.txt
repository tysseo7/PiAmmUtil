Pi Network AMM/DEX Utility Commands

*Command
val.py {token name} -p {address}
●Input
- {token name}: Token name
- {address}: Asset holding address
●Output
- (1) Liquidity Pool Rate for the specified token
- (2) TestPi equivalent balance for the specified asset holding address
- Time graph of (1) and (2) (Time interval: 1 minute)

*Command
candle.py {token name} {ISS address}
●Input
- {token name}: Token name
- {ISS address}: Token issuer address
●Output
- 1-hour candlestick chart for token name/testPi
- Sampling time: 1 minute
