# main.py

import os
import time
import logging
from binance_sdk_spot.spot import Spot, ConfigurationRestAPI, SPOT_REST_API_PROD_URL
from dotenv import load_dotenv
import config

# Load environment variables from .env file
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def main():
    """
    Main function to run the triangular arbitrage bot.
    """
    logging.info("Starting the triangular arbitrage bot...")

    api_key = os.getenv("API_KEY")
    api_secret = os.getenv("API_SECRET")

    if not api_key or not api_secret:
        logging.error("API key and secret not found in .env file.")
        return

    # Create configuration for the REST API
    configuration_rest_api = ConfigurationRestAPI(
        api_key=os.getenv("API_KEY", ""),
        api_secret=os.getenv("API_SECRET", ""),
        base_path=os.getenv("BASE_PATH", SPOT_REST_API_PROD_URL),
    )

    # Initialize Spot client
    client = Spot(config_rest_api=configuration_rest_api)

    while True:
        try:
            start_time = time.time()
            logging.info("Checking for arbitrage opportunities...")
            check_arbitrage_opportunity(client)
            end_time = time.time()
            logging.info(f"Arbitrage check cycle finished in {end_time - start_time:.2f} seconds.")
            time.sleep(config.RATE_LIMITING_DELAY)
        except Exception as e:
            logging.error(f"An error occurred: {e}")
            time.sleep(config.RATE_LIMITING_DELAY)

def get_price(client, symbol):
    """
    Get the latest price for a symbol.
    """
    try:
        response = client.market_data.get_ticker_price(symbol=symbol)
        return float(response.data.price)
    except Exception as e:
        logging.error(f"Error getting price for {symbol}: {e}")
        return None

def check_arbitrage_opportunity(client):
    """
    Check for triangular arbitrage opportunities.
    """
    # Path 1: FDUSD → BTC → USDT → FDUSD
    try:
        price_btc_fdusd = get_price(client, f"{config.INTERMEDIATE_CURRENCY}{config.BASE_CURRENCY}")
        price_btc_usdt = get_price(client, f"{config.INTERMEDIATE_CURRENCY}{config.THIRD_CURRENCY}")
        price_usdt_fdusd = get_price(client, f"{config.THIRD_CURRENCY}{config.BASE_CURRENCY}")

        if price_btc_fdusd and price_btc_usdt and price_usdt_fdusd:
            # Trade amount in BTC
            amount_btc = config.TRADE_AMOUNT / price_btc_fdusd
            # Trade amount in USDT
            amount_usdt = amount_btc * price_btc_usdt
            # Final amount in FDUSD
            final_amount = amount_usdt * price_usdt_fdusd

            # Calculate profit/loss
            profit_loss = final_amount - config.TRADE_AMOUNT
            profit_loss_percent = (profit_loss / config.TRADE_AMOUNT) * 100

            logging.info(f"Path 1: FDUSD -> BTC -> USDT -> FDUSD | Profit/Loss: {profit_loss:.2f} {config.BASE_CURRENCY} ({profit_loss_percent:.4f}%)")

            if profit_loss_percent > config.MIN_PROFIT_THRESHOLD:
                logging.info(f"Arbitrage opportunity found! Profit: {profit_loss_percent:.4f}%")
                execute_trade(client, "PATH_1", price_btc_fdusd, price_btc_usdt, price_usdt_fdusd)
    except Exception as e:
        logging.error(f"Error in Path 1 calculation: {e}")


    # Path 2: FDUSD → USDT → BTC → FDUSD
    try:
        price_usdt_fdusd = get_price(client, f"{config.THIRD_CURRENCY}{config.BASE_CURRENCY}")
        price_btc_usdt = get_price(client, f"{config.INTERMEDIATE_CURRENCY}{config.THIRD_CURRENCY}")
        price_btc_fdusd = get_price(client, f"{config.INTERMEDIATE_CURRENCY}{config.BASE_CURRENCY}")

        if price_usdt_fdusd and price_btc_usdt and price_btc_fdusd:
            # Trade amount in USDT
            amount_usdt = config.TRADE_AMOUNT / price_usdt_fdusd
            # Trade amount in BTC
            amount_btc = amount_usdt / price_btc_usdt
            # Final amount in FDUSD
            final_amount = amount_btc * price_btc_fdusd

            # Calculate profit/loss
            profit_loss = final_amount - config.TRADE_AMOUNT
            profit_loss_percent = (profit_loss / config.TRADE_AMOUNT) * 100

            logging.info(f"Path 2: FDUSD -> USDT -> BTC -> FDUSD | Profit/Loss: {profit_loss:.2f} {config.BASE_CURRENCY} ({profit_loss_percent:.4f}%)")

            if profit_loss_percent > config.MIN_PROFIT_THRESHOLD:
                logging.info(f"Arbitrage opportunity found! Profit: {profit_loss_percent:.4f}%")
                execute_trade(client, "PATH_2", price_usdt_fdusd, price_btc_usdt, price_btc_fdusd)
    except Exception as e:
        logging.error(f"Error in Path 2 calculation: {e}")

def execute_trade(client, path, price1, price2, price3):
    """
    Execute the triangular arbitrage trades.
    """
    if config.DRY_RUN:
        logging.info("Dry run mode is enabled. No real trades will be executed.")
        return

    try:
        # Balance verification
        response = client.rest_api.get_account()
        balances = response.data.balances
        balance_fdusd = next((b for b in balances if b.asset == config.BASE_CURRENCY), None)

        if not balance_fdusd or float(balance_fdusd.free) < config.TRADE_AMOUNT:
            logging.error("Insufficient balance to execute trades.")
            return

        balance_fdusd = float(balance_fdusd.free)


        if path == "PATH_1":
            # FDUSD -> BTC
            order1_response = client.trade.new_order(symbol=f"{config.INTERMEDIATE_CURRENCY}{config.BASE_CURRENCY}", side="BUY", type="MARKET", quantity=config.TRADE_AMOUNT / price1)
            order1 = order1_response.data
            logging.info(f"Order 1 executed: {order1}")
            # BTC -> USDT
            order2_response = client.trade.new_order(symbol=f"{config.INTERMEDIATE_CURRENCY}{config.THIRD_CURRENCY}", side="SELL", type="MARKET", quantity=float(order1.executed_qty))
            order2 = order2_response.data
            logging.info(f"Order 2 executed: {order2}")
            # USDT -> FDUSD
            order3_response = client.trade.new_order(symbol=f"{config.THIRD_CURRENCY}{config.BASE_CURRENCY}", side="BUY", type="MARKET", quantity=float(order2.cummulative_quote_qty))
            order3 = order3_response.data
            logging.info(f"Order 3 executed: {order3}")
        elif path == "PATH_2":
            # FDUSD -> USDT
            order1_response = client.trade.new_order(symbol=f"{config.THIRD_CURRENCY}{config.BASE_CURRENCY}", side="BUY", type="MARKET", quantity=config.TRADE_AMOUNT / price1)
            order1 = order1_response.data
            logging.info(f"Order 1 executed: {order1}")
            # USDT -> BTC
            order2_response = client.trade.new_order(symbol=f"{config.INTERMEDIATE_CURRENCY}{config.THIRD_CURRENCY}", side="BUY", type="MARKET", quantity=float(order1.cummulative_quote_qty) / price2)
            order2 = order2_response.data
            logging.info(f"Order 2 executed: {order2}")
            # BTC -> FDUSD
            order3_response = client.trade.new_order(symbol=f"{config.INTERMEDIATE_CURRENCY}{config.BASE_CURRENCY}", side="SELL", type="MARKET", quantity=float(order2.executed_qty))
            order3 = order3_response.data
            logging.info(f"Order 3 executed: {order3}")

        # Log actual profit
        response = client.rest_api.get_account()
        balances = response.data.balances
        final_balance = next((b for b in balances if b.asset == config.BASE_CURRENCY), None)
        actual_profit = float(final_balance.free) - balance_fdusd
        logging.info(f"Actual profit: {actual_profit:.2f} {config.BASE_CURRENCY}")
    except Exception as e:
        logging.error(f"Error executing trades: {e}")
        # Simple rollback mechanism
        try:
            response = client.rest_api.get_account()
            balances = response.data.balances
            if 'order1' in locals() and order1:
                balance_btc = next((b for b in balances if b.asset == config.INTERMEDIATE_CURRENCY), None)
                if balance_btc and float(balance_btc.free) > 0:
                    client.trade.new_order(symbol=f"{config.INTERMEDIATE_CURRENCY}{config.BASE_CURRENCY}", side="SELL", type="MARKET", quantity=float(balance_btc.free))
                    logging.info("Rollback: Sold BTC back to FDUSD")
            if 'order2' in locals() and order2:
                balance_usdt = next((b for b in balances if b.asset == config.THIRD_CURRENCY), None)
                if balance_usdt and float(balance_usdt.free) > 0:
                    client.trade.new_order(symbol=f"{config.THIRD_CURRENCY}{config.BASE_CURRENCY}", side="SELL", type="MARKET", quantity=float(balance_usdt.free))
                    logging.info("Rollback: Sold USDT back to FDUSD")
        except Exception as rollback_e:
            logging.error(f"Rollback failed: {rollback_e}")

if __name__ == "__main__":
    main()
