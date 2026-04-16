import requests

def fetch_onchain_metrics():
    url = "https://community-api.coinmetrics.io/v4/timeseries/asset-metrics?assets=btc&metrics=AdrActCnt,FlowInExNtv,FlowOutExNtv&frequency=1d&limit_per_asset=3"
    response = requests.get(url)
    data = response.json()
    metrics = data['data'][-1]
    active_addresses = int(metrics['AdrActCnt'])
    exchange_inflow_btc = float(metrics['FlowInExNtv'])
    exchange_outflow_btc = float(metrics['FlowOutExNtv'])
    net_exchange_flow_btc = exchange_outflow_btc - exchange_inflow_btc
    return {"active_addresses": active_addresses, "exchange_inflow_btc": exchange_inflow_btc, "exchange_outflow_btc": exchange_outflow_btc, "net_exchange_flow_btc": net_exchange_flow_btc}
