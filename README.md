# Intro to Observability: OpenTelemetry in Python

This application is here for you to try out tracing.
It consists of a microservice that calls itself, so you can simulate
a whole microservice ecosystem with just one service!

## What to do

Remix this app on Glitch.

### 1. Autoinstrument!

...

#### Configure the Agent

Finally, tell the agent how to send events to Honeycomb.
In `.env` in glitch or your run configuration in IntelliJ, add these
environment variables:

```
HONEYCOMB_API_KEY=replace-this-with-a-real-api-key
HONEYCOMB_DATASET=otel-python
SERVICE_NAME=fibonacci-microservice
SAMPLE_RATE=1
```

Get a Honeycomb API Key from your Team Settings in [Honeycomb](https://ui.honeycomb.io).
(find this by clicking on your profile in the lower-left corner.)

You can name the Honeycomb Dataset anything you want.

You can choose any Service Name you want.

The Sample Rate determines how many requests each saved trace represents; 1 means "keep all of them." Right now you want all of them.

#### See the results

Run the app. Activate the sequence of numbers.
Go to [Honeycomb](https://ui.honeycomb.io) and choose the Dataset you configured.

How many traces are there?

How many spans are in the traces?

Why are there so many??

Which trace has the most, and why is it different?

## 2. Customize a span

Let's make it easier to see what the "index" query parameter is.

To do this, change the code using the OpenTelemetry API.

...

Restart the app, make the sequence go, and find that field on the new spans.

Can you make the trace waterfall view show the index? What pattern does it show?

## 3. Create a custom span

Make the calculation into its own span, to see how much of the time spent on
this service is the meat: adding the fibonacci numbers.

...

After a restart, do your traces show this extra span? Do you see the name of your method?
What percentage of the service time is spend in it?

