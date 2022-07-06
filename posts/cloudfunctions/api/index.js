"use strict";

const express = require("express");
const cors = require("cors");
const app = express();
const posts = require("./posts");


app.use(express.json());
app.use(cors());
app.options(function (_req, res, next) {
    res.header("Access-Control-Allow-Methods", "GET, POST");
    res.header("Access-Control-Allow-Origin", "*");
    res.header("Access-Control-Allow-Headers", "Origin, Content-Type");
    next();
});

app.use("/posts", posts.postsRouter);

module.exports = {
    app,
};