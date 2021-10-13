class ParallelWSClient:
    def __init__(self, ws_host: str, ws_timeout: float, auth_token: str):
        self._ws_host = ws_host
        self._ws_timeout = ws_timeout
        self.__token = auth_token
        logger.info(f"Initialized ParallelWSClient: {self._ws_host}")

    async def subscribe_to_market_data(self, symbol: str, quantities: List[float]):
        websocket = None
        extra_headers = {"Authorization": f"Token {self.__token}"}
        try:
            websocket = await websockets.connect(
                self._ws_host,
                ping_interval=10,
                ping_timeout=self._ws_timeout / 1_000,
                close_timeout=5,
                extra_headers=extra_headers,
            )
            logger.info(f"ParallelOtcWSClient connected")

            subscription_request = {
                "request": "quotes",
                "symbol": symbol,
                "quantities": quantities,
            }
            logger.info(subscription_request)
            await websocket.send(json.dumps(subscription_request))
            raw_response = await websocket.recv()
            response = json.loads(raw_response)
            logger.info(response)
            if not response["success"]:
                logger.error(
                    f"Failed to connect to {symbol} market data. Errors: {response['errors']}"
                )
                websocket.close()
                return
        except Exception as err:
            logger.exception(err)
        return websocket

    async def connect_to_market_data(self, symbol: str, quantities: List[float]):
        websocket = await self.subscribe_to_market_data(symbol, quantities)
        while True:
            try:
                while not websocket or not websocket.open:
                    await asyncio.sleep(1)
                    logger.warning(
                        f"Market data websocket connection dropped, reconnecting..."
                    )
                    websocket = await self.subscribe_to_market_data(symbol, quantities)
                message = await asyncio.wait_for(
                    websocket.recv(), self._ws_timeout / 1_000
                )
                received_quotes = json.loads(message)
                logger.info(received_quotes)
            except asyncio.TimeoutError:
                pass
            except Exception as err:
                logger.exception(err)

    def main(self):
        loop = asyncio.get_event_loop()
        try:
            asyncio.set_event_loop(loop)
            loop.create_task(self.connect_to_market_data("BTC/USD", ["1", "5"]))
            loop.run_forever()
            loop.close()
        except Exception as err:
            logger.exception(err)
        finally:
            loop.stop()


if __name__ == "__main__":
    import os

    auth_token = os.getenv("PARALLEL_AUTH_TOKEN")
    parallel_ws = ParallelWSClient(
        "wss://trade-ws.parallelcapital.co/v1/quotes", 1000, auth_token
    )
    parallel_ws.main()

