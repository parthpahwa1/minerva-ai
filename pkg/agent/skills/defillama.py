import requests
from typing import Optional
from langchain.tools import BaseTool


class ChainFeesTool(BaseTool):
    name: str = "defi_llama_fees_overview"
    description: str = (
        "Fetches fees and revenue information for a specified blockchain from DeFi Llama's API. "
        "Allows configuration of parameters such as excluding chart data and specifying data types."
        "Parameters: chain: str"
    )

    def _run(
        self,
        chain: str,
        exclude_total_data_chart: Optional[bool] = True,
        exclude_total_data_chart_breakdown: Optional[bool] = True,
        data_type: Optional[str] = "dailyFees",
        currency: str = "$",
    ) -> str:
        if not chain:
            return "Chain fee not available"

        base_url = f"https://api.llama.fi/overview/fees/{chain}"
        params = {
            "excludeTotalDataChart": "true" if exclude_total_data_chart else "false",
            "excludeTotalDataChartBreakdown": (
                "true" if exclude_total_data_chart_breakdown else "false"
            ),
        }
        if data_type:
            params["dataType"] = data_type

        response = requests.get(base_url, params=params)
        if response.status_code != 200:
            return f"Error fetching chain fee for {chain} from DefiLlama: HTTP {response.status_code}: {response.text}"

        data = response.json()

        # Extract and format chain summary
        chain_name = data.get("chain", chain)
        total24h = data.get("total24h", "N/A")
        total7d = data.get("total7d", "N/A")
        total30d = data.get("total30d", "N/A")
        change_1d = data.get("change_1d", "N/A")
        change_7d = data.get("change_7d", "N/A")
        change_1m = data.get("change_1m", "N/A")

        result = (
            f"Chain: {chain_name}\n"
            f"24h Fees/Revenue: {currency}{total24h}\n"
            f"7d Total Fees/Revenue: {currency}{total7d}\n"
            f"30d Total Fees/Revenue: {currency}{total30d}\n"
            f"1d Change: {change_1d}%\n"
            f"7d Change: {change_7d}%\n"
            f"1m Change: {change_1m}%\n"
        )

        return result

    async def _arun(
        self,
        chain: str,
        exclude_total_data_chart: Optional[bool] = True,
        exclude_total_data_chart_breakdown: Optional[bool] = True,
        data_type: Optional[str] = None,
    ) -> str:
        return self._run(
            chain,
            exclude_total_data_chart,
            exclude_total_data_chart_breakdown,
            data_type,
        )


class ProtocolFeesTool(BaseTool):
    name: str = "protocol_fees_tool"
    description: str = (
        "Fetches summary of protocol fees and revenue information from DeFi Llama's API, including historical data. "
        "Requires protocol slug as input and allows specifying data type (default: dailyFees)."
    )

    def _run(
        self, protocol: str, data_type: Optional[str] = "dailyFees", currency: str = "$"
    ) -> str:
        if not protocol:
            return "Protocol fee not available"

        base_url = f"https://api.llama.fi/summary/fees/{protocol}"
        params = {"dataType": data_type}

        response = requests.get(base_url, params=params)
        if response.status_code != 200:
            return f"Error fetching protocol fee for {protocol} from DefiLlama: HTTP {response.status_code}: {response.text}"

        data = response.json()

        # Extract and format protocol summary
        protocol_name = data.get("name", protocol)
        description = data.get("description", "No description available.")
        total24h = data.get("total24h", "N/A")
        total7d = data.get("total7d", "N/A")
        total_all_time = data.get("totalAllTime", "N/A")

        result = (
            f"Protocol: {protocol_name}\n"
            f"Description: {description}\n"
            f"24h Fees/Revenue: {currency}{total24h}\n"
            f"7d Total Fees/Revenue: {currency}{total7d}\n"
            f"All-Time Total: {currency}{total_all_time}\n"
        )

        return result

    async def _arun(self, protocol: str, data_type: Optional[str] = "dailyFees") -> str:
        return self._run(protocol, data_type)


class CoinPercentageChangeTool(BaseTool):
    name: str = "coin_percentage_change_tool"
    description: str = (
        "Fetches the percentage change in price for a specified coin over a given period. "
        "Requires a coin identifier (chain:address) and allows specifying timestamp, lookForward, and period."
        "Input paramneters: chain: str, contract_address: str,"
    )

    def _run(
        self,
        chain: str,
        contract_address: str,
        look_forward: Optional[bool] = False,
        period: Optional[str] = "24h",
    ) -> str:
        if not chain or not contract_address:
            return "Error: Coin parameter is required."

        coin = f"{chain}:{contract_address}"
        base_url = f"https://coins.llama.fi/percentage/{coin}"
        params = {
            "lookForward": "true" if look_forward else "false",
            "period": period,
        }

        response = requests.get(base_url, params=params)
        if response.status_code != 200:
            return f"Error fetching % change for {coin} from DefiLlama: HTTP {response.status_code}: {response.text}"

        data = response.json()

        # Extract and format percentage change
        percentage_change = data.get("coins", {}).get(coin, None)
        if not percentage_change:
            return f"Coin percentage change not available"

        result = (
            f"Coin: {coin}\n" f"Percentage Change ({period}): {percentage_change}%\n"
        )

        return result

    async def _arun(
        self,
        chain: str,
        contract_address: str,
        look_forward: Optional[bool] = False,
        period: Optional[str] = "24h",
    ) -> str:
        return self._run(chain, contract_address, look_forward, period)


class ProtocolTVLTool(BaseTool):
    name: str = "protocol_tvl_tool"
    description: str = (
        "Fetches the current Total Value Locked (TVL) of a specified protocol from DeFi Llama's API. "
        "Requires the protocol slug as input."
    )

    def _run(self, protocol: str, currency: str = "$") -> str:
        if not protocol:
            return "Protocol TVL not availble."

        base_url = f"https://api.llama.fi/tvl/{protocol}"

        response = requests.get(base_url)
        if response.status_code != 200:
            return f"Error fetching protocol tvl for {protocol} from DefiLlama: HTTP {response.status_code}: {response.text}"

        tvl = response.json()

        if tvl is None:
            return "Protocol TVL not availble"

        result = f"Protocol: {protocol}\nCurrent TVL: {currency}{tvl}"

        return result

    async def _arun(self, protocol: str) -> str:
        return self._run(protocol)
