from fastapi import FastAPI
import yfinance as yf
import pandas as pd
import json
app = FastAPI()

# health check and version
@app.get("/health")
def health_check():
    return {"status": "ok", "version": "1.0.0"}


@app.get("/stock/{symbol}")
def get_stock(symbol: str):
    stock = yf.Ticker(symbol)
    income_statement = stock.income_stmt
    balance_sheet = stock.balance_sheet
    cash_flow = stock.cashflow
    stock_info = stock.info

    income_statement_df = pd.DataFrame(income_statement)
    # balance_sheet_df = pd.DataFrame(balance_sheet)
    # cash_flow_df = pd.DataFrame(cash_flow)

    # print('Net Income==>')
    first_column = income_statement_df.columns.tolist()[0]
    # print(income_statement_df[first_column]['Net Income'])

    net_income = income_statement_df[first_column]['Net Income']
    # print(net_income)

    operating_income = income_statement_df[first_column]['Operating Income']
    # print(operating_income)

    operating_expense = income_statement_df[first_column]['Operating Expense']
    # print(operating_expense)

    gross_profit = income_statement_df[first_column]['Gross Profit']
    # print(gross_profit)

    cost_of_revenue = income_statement_df[first_column]['Cost Of Revenue']
    # print(cost_of_revenue)

    revenue = income_statement_df[first_column]['Total Revenue']
    # print(revenue)

    # EBITDA
    ebitda = income_statement_df[first_column]['EBITDA']
    # print(ebitda)

    # short_interest
    short_interest = stock_info['shortPercentOfFloat']
    # print(short_interest)

    # held_percent_insiders
    held_percent_insiders = stock_info['heldPercentInsiders']
    # print(held_percent_insiders)

    held_percent_institutions = stock_info['heldPercentInstitutions']
    # print(held_percent_institutions)

    shares_outstanding = stock_info['sharesOutstanding']
    # print(shares_outstanding)

    # cash and depth
    total_cash = stock_info['totalCash']
    # print(total_cash)

    total_debt = stock_info['totalDebt']
    # print(total_debt)

    current_price = stock_info['currentPrice']
    # print(current_price)

    target_high_price = stock_info['targetHighPrice']
    # print(target_high_price)

    target_low_price = stock_info['targetLowPrice']
    # print(target_low_price)

    target_mean_price = stock_info['targetMeanPrice']
    # print(target_mean_price)

    forward_pe = stock_info['forwardPE']
    # print(forward_pe)

    trailing_pe = stock_info['trailingPE']
    # print(trailing_pe)

    pe_ratio = stock_info['trailingPE']
    # print(pe_ratio)

    market_cap = stock_info['marketCap']
    # print(market_cap)

    # volume
    volume = stock_info['volume']
    # print(volume)

    # averageVolume
    average_volume = stock_info['averageVolume']
    # print(average_volume)

    # fiftyTwoWeekLow
    fifty_two_week_low = stock_info['fiftyTwoWeekLow']
    # print(fifty_two_week_low)

    # fiftyTwoWeekHigh
    fifty_two_week_high = stock_info['fiftyTwoWeekHigh']
    # print(fifty_two_week_high)

    # regularMarketChangePercent
    regular_market_change_percent = stock_info['regularMarketChangePercent']
    # print(regular_market_change_percent)

    # regularMarketChange
    regular_market_change = stock_info['regularMarketChange']
    # print(regular_market_change)

    # regularMarketPrice
    regular_market_price = stock_info['regularMarketPrice']
    # print(regular_market_price)

    # Symbol
    symbol = stock_info['symbol']
    # print(symbol)

    return {
        # "income_statement": json.loads(income_statement_df.to_json()),
        # "balance_sheet": json.loads(balance_sheet_df.to_json()),
        # "cash_flow": json.loads(cash_flow_df.to_json()),
        # "stock_info": stock_info

        "net_income": net_income,
        "operating_income": operating_income,
        "operating_expense": operating_expense,
        "gross_profit": gross_profit,
        "cost_of_revenue": cost_of_revenue,
        "revenue": revenue,
        "ebitda": ebitda,
        "short_interest": short_interest,
        "held_percent_insiders": held_percent_insiders,
        "held_percent_institutions": held_percent_institutions,
        "shares_outstanding": shares_outstanding,
        "total_cash": total_cash,
        "total_debt": total_debt,
        "current_price": current_price,
        "target_high_price": target_high_price,
        "target_low_price": target_low_price,
        "target_mean_price": target_mean_price,
        "forward_pe": forward_pe,
        "trailing_pe": trailing_pe,
        "pe_ratio": pe_ratio,
        "market_cap": market_cap,
        "volume": volume,
        "average_volume": average_volume,
        "fifty_two_week_low": fifty_two_week_low,
        "fifty_two_week_high": fifty_two_week_high,
        "regular_market_change_percent": regular_market_change_percent,
        "regular_market_change": regular_market_change,
        "regular_market_price": regular_market_price,
        "symbol": symbol,
    }


