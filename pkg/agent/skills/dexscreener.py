import statistics
import requests
from langchain.tools import BaseTool
from rapidfuzz import fuzz, process


class DexscreenerTokenLiquidityTool(BaseTool):
    """
    Fetches liquidity and market metrics for a specified token_name from DexScreener's API.
    Returns a small JSON-friendly dictionary containing median metrics (FDV, marketCap, liquidity),
    and the single most active pair (highest transaction count).
    """

    name: str = "dexscreener_token_liquidity_metrics"
    description: str = (
        "Fetches liquidity and market metrics for a specified token_name from DexScreener's API. "
        "Calculates median FDV, marketCap, liquidity.usd across all pairs, and returns the most active pair. "
        "Parameters: token_name: str"
    )

    def _run(self, token_name: str) -> dict:
        """
        Synchronous method to get token liquidity metrics as a minimal dictionary.

        :param token_address: (str) The token contract address to query.
        :return: A JSON-friendly dictionary with median metrics and the most active pair.
        """
        if not token_name:
            return {"error": "No token address was provided."}

        url = f"https://api.dexscreener.com/latest/dex/search/?q={token_name}"
        try:
            response = requests.get(url)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            return {"error": f"Error fetching token data from DexScreener: {str(e)}"}

        data = response.json()
        pairs = data.get("pairs", [])
        if not pairs:
            return {"error": f"No pair data found for token address: {token_name}"}

        # Collect metrics for median calculations
        fdv_values = []
        mcap_values = []
        liquidity_usd_values = []

        # Track the most active pair (based on highest h24 transaction count)
        most_active_pair = {}

        for pair in pairs:
            fdv = pair.get("fdv", None)
            market_cap = pair.get("marketCap", None)
            liquidity_usd = pair.get("liquidity", {}).get("usd", None)
            chain_id = pair.get("chainId", "")

            formatted_pair = {
                "chain": pair.get("chainId", ""),
                "fdv": pair.get("fdv", None),
                "market_cap": pair.get("marketCap", None),
                "liquidity": pair.get("liquidity", {}),
                "info": pair.get("info", {}),
                "baseToken": pair.get("baseToken", {}),
            }
            # Collect FDV, MCap, Liquidity if available and numeric
            if isinstance(fdv, (int, float)):
                fdv_values.append(fdv)
            if isinstance(market_cap, (int, float)):
                mcap_values.append(market_cap)
            if isinstance(liquidity_usd, (int, float)):
                liquidity_usd_values.append(liquidity_usd)

            base_token = pair.get("baseToken", {}).get("name", "")
            score = fuzz.ratio(base_token.lower(), token_name.lower())

            if score > most_active_pair.get(chain_id, {}).get(score, 0):
                most_active_pair[chain_id] = {
                    "score": score,
                    "formatted_pair": formatted_pair,
                }

        # Compute medians safely, default to 0 if no numeric data
        median_fdv = statistics.median(fdv_values) if fdv_values else 0
        median_market_cap = statistics.median(mcap_values) if mcap_values else 0
        median_liquidity_usd = (
            statistics.median(liquidity_usd_values) if liquidity_usd_values else 0
        )

        # Format the final output
        if not most_active_pair:
            return {
                "medianFDV": median_fdv,
                "medianMarketCap": median_market_cap,
                "medianLiquidityUsd": median_liquidity_usd,
                "mostActivePair": None,
            }

        return {
            "medianFDV": median_fdv,
            "medianMarketCap": median_market_cap,
            "medianLiquidityUsd": median_liquidity_usd,
            "mostActivePair": most_active_pair,
        }

    async def _arun(self, token_name: str) -> dict:
        """
        Asynchronous version of `_run`.
        """
        return self._run(token_name)
