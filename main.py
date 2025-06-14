from fastapi import FastAPI, HTTPException, Body
import yfinance as yf
import pandas as pd
from typing import Dict, Any, Optional, TypedDict, List, Union
from pydantic import BaseModel, Field
from fastapi.middleware.cors import CORSMiddleware
import redis
import json
import os

app = FastAPI()

# Initialize Redis client with environment variables
redis_host = os.getenv('REDIS_HOST', 'localhost')
redis_port = int(os.getenv('REDIS_PORT', 6379))
redis_client = redis.Redis(
    host=redis_host,
    port=redis_port,
    db=0,
    decode_responses=True
)

# Cache expiration time (12 hours in seconds)
CACHE_EXPIRATION = 12 * 60 * 60

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

class StockSymbolsRequest(BaseModel):
    symbols: List[str] = Field(..., example=["AAPL", "GOOGL", "MSFT"])

class StocksResponse(BaseModel):
    stocks: List[StockResponse]

# health check and version
@app.get("/health", response_model=HealthResponse)
def health_check() -> HealthResponse:
    return HealthResponse(status="ok", version="1.1.0")

@app.get("/stock/{symbol}", response_model=StockResponse)
def get_stock(symbol: str) -> StockResponse:
    # Check cache first
    cache_key = f"stock:{symbol}"
    cached_data = redis_client.get(cache_key)
    
    if cached_data:
        return StockResponse(**json.loads(cached_data))
        
    try:
        stock: yf.Ticker = yf.Ticker(symbol)
        income_statement: pd.DataFrame = stock.income_stmt
        stock_info: Dict[str, Any] = stock.info
        
        # Check if we got valid stock info
        if not stock_info:
            raise HTTPException(status_code=404, detail=f"Stock data not found for symbol: {symbol}")
            
        stock_name: str = stock_info.get('longName', symbol)

        # Initialize income statement values with None
        net_income = operating_income = operating_expense = None
        gross_profit = cost_of_revenue = revenue = ebitda = None

        # Only process income statement if it exists and has data
        if income_statement is not None and not income_statement.empty:
            income_statement_df: pd.DataFrame = pd.DataFrame(income_statement)
            
            # Safely get income statement values using try/except for each field
            try:
                net_income = income_statement_df.loc['Net Income'].iloc[0]
                net_income = None if pd.isna(net_income) else net_income
            except:
                net_income = None
                
            try:
                operating_income = income_statement_df.loc['Operating Income'].iloc[0]
                operating_income = None if pd.isna(operating_income) else operating_income
            except:
                operating_income = None
                
            try:
                operating_expense = income_statement_df.loc['Operating Expense'].iloc[0]
                operating_expense = None if pd.isna(operating_expense) else operating_expense
            except:
                operating_expense = None
                
            try:
                gross_profit = income_statement_df.loc['Gross Profit'].iloc[0]
                gross_profit = None if pd.isna(gross_profit) else gross_profit
            except:
                gross_profit = None
                
            try:
                cost_of_revenue = income_statement_df.loc['Cost Of Revenue'].iloc[0]
                cost_of_revenue = None if pd.isna(cost_of_revenue) else cost_of_revenue
            except:
                cost_of_revenue = None
                
            try:
                revenue = income_statement_df.loc['Total Revenue'].iloc[0]
                revenue = None if pd.isna(revenue) else revenue
            except:
                revenue = None
                
            try:
                ebitda = income_statement_df.loc['EBITDA'].iloc[0]
                ebitda = None if pd.isna(ebitda) else ebitda
            except:
                ebitda = None

        # Initialize recommendations with default values
        recommendations_model = RecommendationsModel(
            strongBuy=0,
            buy=0,
            hold=0,
            sell=0
        )

        # Safely get recommendations
        try:
            recommendations_df: pd.DataFrame = stock.recommendations
            if recommendations_df is not None and not recommendations_df.empty:
                filtered_recommendations = recommendations_df.loc[
                    recommendations_df['period'] == '0m', 
                    ['strongBuy', 'buy', 'hold', 'sell']
                ]
                if not filtered_recommendations.empty:
                    values = filtered_recommendations.values.flatten()
                    recommendations_model = RecommendationsModel(
                        strongBuy=int(values[0]) if not pd.isna(values[0]) else 0,
                        buy=int(values[1]) if not pd.isna(values[1]) else 0,
                        hold=int(values[2]) if not pd.isna(values[2]) else 0,
                        sell=int(values[3]) if not pd.isna(values[3]) else 0
                    )
        except Exception as e:
            print(f"Error processing recommendations: {str(e)}")
            # Continue with default recommendations

        response = StockResponse(
            stock_name=stock_name,
            recommendations=recommendations_model,
            net_income=net_income,
            operating_income=operating_income,
            operating_expense=operating_expense,
            gross_profit=gross_profit,
            cost_of_revenue=cost_of_revenue,
            revenue=revenue,
            ebitda=ebitda,
            short_interest=stock_info.get('shortPercentOfFloat'),
            held_percent_insiders=stock_info.get('heldPercentInsiders'),
            held_percent_institutions=stock_info.get('heldPercentInstitutions'),
            shares_outstanding=stock_info.get('sharesOutstanding'),
            total_cash=stock_info.get('totalCash'),
            total_debt=stock_info.get('totalDebt'),
            current_price=stock_info.get('currentPrice'),
            target_high_price=stock_info.get('targetHighPrice'),
            target_low_price=stock_info.get('targetLowPrice'),
            target_mean_price=stock_info.get('targetMeanPrice'),
            forward_pe=stock_info.get('forwardPE'),
            trailing_pe=stock_info.get('trailingPE'),
            pe_ratio=stock_info.get('trailingPE'),
            market_cap=stock_info.get('marketCap'),
            volume=stock_info.get('volume'),
            average_volume=stock_info.get('averageVolume'),
            fifty_two_week_low=stock_info.get('fiftyTwoWeekLow'),
            fifty_two_week_high=stock_info.get('fiftyTwoWeekHigh'),
            regular_market_change_percent=stock_info.get('regularMarketChangePercent'),
            regular_market_change=stock_info.get('regularMarketChange'),
            regular_market_price=stock_info.get('regularMarketPrice'),
            symbol=stock_info.get('symbol', symbol)
        )
        
        # Cache the response
        redis_client.setex(
            cache_key,
            CACHE_EXPIRATION,
            json.dumps(response.dict())
        )
        
        return response
    except Exception as e:
        print(f"Error retrieving stock data: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error retrieving stock data: {str(e)}")

@app.post("/stocks", response_model=StocksResponse)
def get_multiple_stocks(request: StockSymbolsRequest = Body(...)) -> StocksResponse:
    responses = []
    for symbol in request.symbols:
        # Check cache first
        cache_key = f"stock:{symbol}"
        cached_data = redis_client.get(cache_key)
        if cached_data:
            try:
                responses.append(StockResponse(**json.loads(cached_data)))
                continue
            except Exception:
                pass  # fallback to fetching if cache is corrupted
        try:
            stock: yf.Ticker = yf.Ticker(symbol)
            income_statement: pd.DataFrame = stock.income_stmt
            stock_info: Dict[str, Any] = stock.info
            if not stock_info:
                continue  # skip if not found
            stock_name: str = stock_info.get('longName', symbol)
            net_income = operating_income = operating_expense = None
            gross_profit = cost_of_revenue = revenue = ebitda = None
            if income_statement is not None and not income_statement.empty:
                income_statement_df: pd.DataFrame = pd.DataFrame(income_statement)
                try:
                    net_income = income_statement_df.loc['Net Income'].iloc[0]
                    net_income = None if pd.isna(net_income) else net_income
                except:
                    net_income = None
                try:
                    operating_income = income_statement_df.loc['Operating Income'].iloc[0]
                    operating_income = None if pd.isna(operating_income) else operating_income
                except:
                    operating_income = None
                try:
                    operating_expense = income_statement_df.loc['Operating Expense'].iloc[0]
                    operating_expense = None if pd.isna(operating_expense) else operating_expense
                except:
                    operating_expense = None
                try:
                    gross_profit = income_statement_df.loc['Gross Profit'].iloc[0]
                    gross_profit = None if pd.isna(gross_profit) else gross_profit
                except:
                    gross_profit = None
                try:
                    cost_of_revenue = income_statement_df.loc['Cost Of Revenue'].iloc[0]
                    cost_of_revenue = None if pd.isna(cost_of_revenue) else cost_of_revenue
                except:
                    cost_of_revenue = None
                try:
                    revenue = income_statement_df.loc['Total Revenue'].iloc[0]
                    revenue = None if pd.isna(revenue) else revenue
                except:
                    revenue = None
                try:
                    ebitda = income_statement_df.loc['EBITDA'].iloc[0]
                    ebitda = None if pd.isna(ebitda) else ebitda
                except:
                    ebitda = None
            recommendations_model = RecommendationsModel(
                strongBuy=0,
                buy=0,
                hold=0,
                sell=0
            )
            try:
                recommendations_df: pd.DataFrame = stock.recommendations
                if recommendations_df is not None and not recommendations_df.empty:
                    filtered_recommendations = recommendations_df.loc[
                        recommendations_df['period'] == '0m', 
                        ['strongBuy', 'buy', 'hold', 'sell']
                    ]
                    if not filtered_recommendations.empty:
                        values = filtered_recommendations.values.flatten()
                        recommendations_model = RecommendationsModel(
                            strongBuy=int(values[0]) if not pd.isna(values[0]) else 0,
                            buy=int(values[1]) if not pd.isna(values[1]) else 0,
                            hold=int(values[2]) if not pd.isna(values[2]) else 0,
                            sell=int(values[3]) if not pd.isna(values[3]) else 0
                        )
            except Exception as e:
                print(f"Error processing recommendations for {symbol}: {str(e)}")
            response = StockResponse(
                stock_name=stock_name,
                recommendations=recommendations_model,
                net_income=net_income,
                operating_income=operating_income,
                operating_expense=operating_expense,
                gross_profit=gross_profit,
                cost_of_revenue=cost_of_revenue,
                revenue=revenue,
                ebitda=ebitda,
                short_interest=stock_info.get('shortPercentOfFloat'),
                held_percent_insiders=stock_info.get('heldPercentInsiders'),
                held_percent_institutions=stock_info.get('heldPercentInstitutions'),
                shares_outstanding=stock_info.get('sharesOutstanding'),
                total_cash=stock_info.get('totalCash'),
                total_debt=stock_info.get('totalDebt'),
                current_price=stock_info.get('currentPrice'),
                target_high_price=stock_info.get('targetHighPrice'),
                target_low_price=stock_info.get('targetLowPrice'),
                target_mean_price=stock_info.get('targetMeanPrice'),
                forward_pe=stock_info.get('forwardPE'),
                trailing_pe=stock_info.get('trailingPE'),
                pe_ratio=stock_info.get('trailingPE'),
                market_cap=stock_info.get('marketCap'),
                volume=stock_info.get('volume'),
                average_volume=stock_info.get('averageVolume'),
                fifty_two_week_low=stock_info.get('fiftyTwoWeekLow'),
                fifty_two_week_high=stock_info.get('fiftyTwoWeekHigh'),
                regular_market_change_percent=stock_info.get('regularMarketChangePercent'),
                regular_market_change=stock_info.get('regularMarketChange'),
                regular_market_price=stock_info.get('regularMarketPrice'),
                symbol=stock_info.get('symbol', symbol)
            )
            redis_client.setex(
                cache_key,
                CACHE_EXPIRATION,
                json.dumps(response.dict())
            )
            responses.append(response)
        except Exception as e:
            print(f"Error retrieving stock data for {symbol}: {str(e)}")
            continue
    return StocksResponse(stocks=responses)