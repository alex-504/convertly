# Variables
SASS_INPUT = static/scss/styles.scss
SASS_OUTPUT = static/css/styles.css
FLASK_APP = app.py

# Default task to run the local server and watch SCSS
start: sass-watch flask

# Watch for SCSS changes and compile
sass-watch:
	@echo "Watching for SCSS changes..."
	sass --watch $(SASS_INPUT):$(SASS_OUTPUT) &

# Run the Flask server
flask:
	@echo "Starting Flask server..."
	python $(FLASK_APP)

# Clean the generated CSS file
clean:
	@echo "Cleaning up generated CSS..."
	rm -f $(SASS_OUTPUT)

# Stop all background processes (for Sass)
stop:
	@echo "Stopping background processes..."
	killall sass || true