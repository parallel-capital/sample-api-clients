class ParallelRESTClient:
    def __init__(self, token: str, is_sandbox: bool = False):
        if is_sandbox:
            self.url = "https://trade-sandbox.parallelcapital.co/api/v1"
        else:  # Production!
            self.url = "https://trade.parallelcapital.co/api/v1"
        self.__headers = {
            "Content-Type": "application/json",
            "Authorization": f"Token {token}",
        }

    def fetch_balances(self) -> dict:
        balances = {}
        request_url = f"{self.url}/balances"
        try:
            balances = requests.get(request_url, headers=self.__headers)
            balances.raise_for_status()
        except Exception as err:
            logger.exception(err)
        return balances

    def fetch_transactions(self) -> list:
        transactions = []
        request_url = f"{self.url}/transactions"
        try:
            transactions = requests.get(request_url, headers=self.__headers)
            transactions.raise_for_status()
        except Exception as err:
            logger.exception(err)
        return transactions

    def create_order(
        self,
        side: str,
        symbol: str,
        quantity: float,
        price: float,
        slippage_bps: float,
        customer_order_id: str = str(uuid.uuid4()),
    ) -> dict:
        response = {}
        request_url = f"{self.url}/orders"
        request = {
            "customer_order_id": customer_order_id,
            "side": side,
            "symbol": symbol,
            "quantity": str(quantity),
            "price": str(price),
            "slippage_bps": str(slippage_bps),
            "order_type": "FOK",
        }
        try:
            response = requests.post(request_url, data=request, headers=self.__headers)
            response.raise_for_status()
        except Exception as err:
            logger.exception(err)
        return response

