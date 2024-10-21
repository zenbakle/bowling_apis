from myapp import create_app

c_app = create_app()
app = c_app[0]
games = c_app[1]
if __name__ == '__main__':
    app.run(debug=True)