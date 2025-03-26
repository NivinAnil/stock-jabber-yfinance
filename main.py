from fastapi import FastAPI, HTTPException
import yfinance as yf
import pandas as pd
from typing import Dict, Any, Optional, TypedDict, List, Union
from pydantic import BaseModel, Field
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

class HealthResponse(BaseModel):
    status: str
    version: str

class RecommendationsModel(BaseModel):
    strongBuy: int
    buy: int
    hold: int
    sell: int

class StockResponse(BaseModel):
    stock_name: str
    recommendations: RecommendationsModel
    net_income: Optional[float] = None
    operating_income: Optional[float] = None
    operating_expense: Optional[float] = None
    other_income_expense: Optional[float] = None
    gross_profit: Optional[float] = None
    cost_of_revenue: Optional[float] = None
    revenue: Optional[float] = None
    ebitda: Optional[float] = None
    short_interest: Optional[float] = None
    held_percent_insiders: Optional[float] = None
    held_percent_institutions: Optional[float] = None
    shares_outstanding: Optional[float] = None
    total_cash: Optional[float] = None
    total_debt: Optional[float] = None
    current_price: Optional[float] = None
    target_high_price: Optional[float] = None
    target_low_price: Optional[float] = None
    target_mean_price: Optional[float] = None
    forward_pe: Optional[float] = None
    trailing_pe: Optional[float] = None
    pe_ratio: Optional[float] = None
    market_cap: Optional[float] = None
    volume: Optional[int] = None
    average_volume: Optional[int] = None
    fifty_two_week_low: Optional[float] = None
    fifty_two_week_high: Optional[float] = None
    regular_market_change_percent: Optional[float] = None
    regular_market_change: Optional[float] = None
    regular_market_price: Optional[float] = None
    symbol: str

# health check and version
@app.get("/health", response_model=HealthResponse)
def health_check() -> HealthResponse:
    return HealthResponse(status="ok", version="1.0.0")

@app.get("/stock/{symbol}", response_model=StockResponse)
def get_stock(symbol: str) -> StockResponse:
    try:
        stock: yf.Ticker = yf.Ticker(symbol)
        income_statement: pd.DataFrame = stock.income_stmt
        stock_info: Dict[str, Any] = stock.info
        stock_name: str = stock_info['longName']

        income_statement_df: pd.DataFrame = pd.DataFrame(income_statement)
        
        # Extract data from income statement
        first_column: Any = income_statement_df.columns.tolist()[0]
        
        net_income: float = income_statement_df[first_column]['Net Income']
        operating_income: float = income_statement_df[first_column]['Operating Income']
        operating_expense: float = income_statement_df[first_column]['Operating Expense']
        gross_profit: float = income_statement_df[first_column]['Gross Profit']
        cost_of_revenue: float = income_statement_df[first_column]['Cost Of Revenue']
        revenue: float = income_statement_df[first_column]['Total Revenue']
        ebitda: float = income_statement_df[first_column]['EBITDA']
        other_income_expense: float = income_statement_df[first_column]['Other Income Expense']

        # Extract data from stock info
        short_interest: float = stock_info.get('shortPercentOfFloat')
        held_percent_insiders: float = stock_info.get('heldPercentInsiders')
        held_percent_institutions: float = stock_info.get('heldPercentInstitutions')
        shares_outstanding: float = stock_info.get('sharesOutstanding')
        total_cash: float = stock_info.get('totalCash')
        total_debt: float = stock_info.get('totalDebt')
        current_price: float = stock_info.get('currentPrice')
        target_high_price: float = stock_info.get('targetHighPrice')
        target_low_price: float = stock_info.get('targetLowPrice')
        target_mean_price: float = stock_info.get('targetMeanPrice')
        forward_pe: float = stock_info.get('forwardPE')
        trailing_pe: float = stock_info.get('trailingPE')
        pe_ratio: float = stock_info.get('trailingPE')
        market_cap: float = stock_info.get('marketCap')
        volume: int = stock_info.get('volume')
        average_volume: int = stock_info.get('averageVolume')
        fifty_two_week_low: float = stock_info.get('fiftyTwoWeekLow')
        fifty_two_week_high: float = stock_info.get('fiftyTwoWeekHigh')
        regular_market_change_percent: float = stock_info.get('regularMarketChangePercent')
        regular_market_change: float = stock_info.get('regularMarketChange')
        regular_market_price: float = stock_info.get('regularMarketPrice')
        symbol_value: str = stock_info.get('symbol', symbol)
        
        # Get recommendations
        recommendations_df: pd.DataFrame = stock.recommendations
        filtered_recommendations = recommendations_df.loc[recommendations_df['period'] == '0m', ['strongBuy', 'buy', 'hold', 'sell']].values.flatten()
        recommendations_model = RecommendationsModel(
            strongBuy=int(filtered_recommendations[0]),
            buy=int(filtered_recommendations[1]),
            hold=int(filtered_recommendations[2]),
            sell=int(filtered_recommendations[3])
        )

        return StockResponse(
            stock_name=stock_name,
            recommendations=recommendations_model,
            net_income=net_income,
            operating_income=operating_income,
            operating_expense=operating_expense,
            other_income_expense=other_income_expense,
            gross_profit=gross_profit,
            cost_of_revenue=cost_of_revenue,
            revenue=revenue,
            ebitda=ebitda,
            short_interest=short_interest,
            held_percent_insiders=held_percent_insiders,
            held_percent_institutions=held_percent_institutions,
            shares_outstanding=shares_outstanding,
            total_cash=total_cash,
            total_debt=total_debt,
            current_price=current_price,
            target_high_price=target_high_price,
            target_low_price=target_low_price,
            target_mean_price=target_mean_price,
            forward_pe=forward_pe,
            trailing_pe=trailing_pe,
            pe_ratio=pe_ratio,
            market_cap=market_cap,
            volume=volume,
            average_volume=average_volume,
            fifty_two_week_low=fifty_two_week_low,
            fifty_two_week_high=fifty_two_week_high,
            regular_market_change_percent=regular_market_change_percent,
            regular_market_change=regular_market_change,
            regular_market_price=regular_market_price,
            symbol=symbol_value
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving stock data: {str(e)}")