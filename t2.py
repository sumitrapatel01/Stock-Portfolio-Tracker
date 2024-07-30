from flask import Flask, request, jsonify
import pandas as pd
import yfinance as yf
from datetime import datetime

app = Flask(__name__)

class StockPortfolio:
    def __init__(self):
        self.portfolio = pd.DataFrame(columns=[
            'Stock Symbol', 'Purchase Date', 'Purchase Price', 
            'Number of Shares', 'Current Price', 'Total Investment', 
            'Current Value', 'Gain/Loss'
        ])

    def add_stock(self, symbol, purchase_date, purchase_price, shares):
        try:
            stock = yf.Ticker(symbol)
            current_price = stock.history(period='1d')['Close'].iloc[-1]
            total_investment = purchase_price * shares
            current_value = current_price * shares
            gain_loss = current_value - total_investment

            new_stock = pd.DataFrame([{
                'Stock Symbol': symbol,
                'Purchase Date': purchase_date,
                'Purchase Price': purchase_price,
                'Number of Shares': shares,
                'Current Price': current_price,
                'Total Investment': total_investment,
                'Current Value': current_value,
                'Gain/Loss': gain_loss
            }])

            self.portfolio = pd.concat([self.portfolio, new_stock], ignore_index=True)
            return f"Stock {symbol} added successfully."
        except IndexError:
            return f"Failed to retrieve data for {symbol}. Please check the stock symbol and try again."
        except Exception as e:
            return f"An error occurred: {e}"

    def remove_stock(self, symbol):
        self.portfolio = self.portfolio[self.portfolio['Stock Symbol'] != symbol]
        return f"Stock {symbol} removed successfully."

    def update_prices(self):
        for i, row in self.portfolio.iterrows():
            try:
                stock = yf.Ticker(row['Stock Symbol'])
                current_price = stock.history(period='1d')['Close'].iloc[-1]
                self.portfolio.at[i, 'Current Price'] = current_price
                self.portfolio.at[i, 'Current Value'] = current_price * row['Number of Shares']
                self.portfolio.at[i, 'Gain/Loss'] = self.portfolio.at[i, 'Current Value'] - row['Total Investment']
            except IndexError:
                print(f"Failed to update data for {row['Stock Symbol']}.")
            except Exception as e:
                print(f"An error occurred: {e}")

    def get_portfolio(self):
        self.update_prices()
        return self.portfolio.to_dict(orient='records')

    def portfolio_summary(self):
        self.update_prices()
        total_investment = self.portfolio['Total Investment'].sum()
        total_current_value = self.portfolio['Current Value'].sum()
        total_gain_loss = self.portfolio['Gain/Loss'].sum()
        percentage_gain_loss = (total_gain_loss / total_investment) * 100 if total_investment != 0 else 0

        summary = {
            'Total Investment': total_investment,
            'Total Current Value': total_current_value,
            'Total Gain/Loss': total_gain_loss,
            'Percentage Gain/Loss': percentage_gain_loss
        }

        return summary

portfolio = StockPortfolio()

@app.route('/add_stock', methods=['POST'])
def add_stock():
    data = request.json
    symbol = data['symbol']
    purchase_date = data['purchase_date']
    purchase_price = data['purchase_price']
    shares = data['shares']
    result = portfolio.add_stock(symbol, purchase_date, purchase_price, shares)
    return jsonify({'result': result})

@app.route('/remove_stock', methods=['POST'])
def remove_stock():
    data = request.json
    symbol = data['symbol']
    result = portfolio.remove_stock(symbol)
    return jsonify({'result': result})

@app.route('/portfolio', methods=['GET'])
def get_portfolio():
    return jsonify(portfolio.get_portfolio())

@app.route('/portfolio_summary', methods=['GET'])
def portfolio_summary():
    return jsonify(portfolio.portfolio_summary())

if __name__ == '__main__':
    app.run(debug=True)
