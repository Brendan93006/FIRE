# FIRE Finance
#### Video Demo:  <https://www.youtube.com/watch?v=AfmAVBC4YZE>
#### Description:
FIRE Finance is an application aimed at helping users achieve financial independence and retire early, thus, helping them take control of their future finances. This application amalgamates investing, account management, and planning into one platform for ease of use. The backend is developed using Python and Flask and SQLite is used for data storage. Yahoo Finance API is utilized for realtime stock data. The frontend is developed using HTML and Bootstrap with some JavaScript used in the investing part for dynamic operations.

FIRE Finance enables users to perform stock market operations, manage several accounts, and calculates their FIRE number with an estimate of the duration needed for them to reach financial independence. The application aims to be both informational and functional, offering users practical investment experience and seamless integration of personal finance planning.

Just like in CS50 Finance, the app has a secure registration and login system which allows the user to register for an account, set a unique username and password. The app also securely stores the user’s financial information and ensures that only the account holder can access it. The app uses best practices in security to handle authentication, and the user’s sensitive information is securely stored in a SQLite database.

An integral aspect of the core functionalities of FIRE Finance is the integration of a stock investment and trading feature. Users have the option to browse through the available stocks and see their symbol, company name, and current market price according to yfinance. Users can buy and sell stocks right from their dashboards and the system ensures that the users’ account balances and stock holdings are always current. Very little JavaScript is employed to improve the Investment UI, so that users can select whether they want to buy stocks in shares or dollars.

The FIRE calculator is an interactive and educational calculator in the app. It allows users to enter their net-worth currently, their expected annual expenses, and expected savings amount so they can determine their FIRE number—the amount they require for financial independence. The calculator will also calculate the number of years it will take to obtain FIRE using the user's savings rate currently, safe withdrawal rate, and assumed market returns so users can plan and make sense of things ahead of time.

FIRE Finance provides various kinds of accounts such as Cash, Savings, Brokerage, Retirement, and Health accounts. Each account can be opened, viewed, and managed separately, thus enabling intensive monitoring of the financial situation as a whole. The multiple-account support offers realistic simulation of management of personal finance, which helps users form strategic attitudes towards correct decision-making in real life.

There is also a research feature driven by the Yahoo Finance API within the application. Stocks can be located and discovered with comprehensive information like current market prices, stock symbol, and company name. Users can invest intelligently using the imformation given in the reasearch feature.

FIRE Finance has a history feature to make sure users keep track of their transactions in different accounts and different investing and selling events.

FIRE Finance App is implemented using Python atop the Flask web framework, which provides simplicity, scalability, and flexibility for web application development. The lightweight nature of Flask provides a straightforward way to manage routes, process requests, and communicate with external APIs such as Yahoo Finance. SQLite database is employed for simplicity and trustworthiness and for keeping all user data, transactions, and account details in local storage without the need for database installations. HTML and Bootstrap were employed on the frontend to develop a responsive and neat UI. A small amount of JavaScript is employed to add the option to choose between shares and dollars in the investing interface. The combination of the aforementioned technologies results in a stable and sustainable application.

Upon registration or login, the users can then browse through the app to accomplish different financial activities. They can:

Do research and search for stocks with the in-app stock research tool.

Make buy or sell orders to track their investment portfolio.

Monitor balances of different types of accounts such as Cash, Savings, Brokerage, Retirement, and Health accounts.

Calculate their FIRE number and years until they achieve financial independence.

The interface has been made user-friendly with simple navigation and responsive layouts thanks to Bootstrap.

Possible improvements are incorporating advanced charting of stock performance, increasing the number of financial calculators, incorporating external means of authentication, and incorporating notifications or alerts to portfolio changes. These additions would enhance the app's utility and appeal to users even further.

The app’s authentication along with parts of the invest, sell, history, and research features are inspired by CS50 Finance.

Stock data is provided by the Yahoo Finance API (yfinance).

Development assistance was provided by ChatGPT and GitHub Copilot.
