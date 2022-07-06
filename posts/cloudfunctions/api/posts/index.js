const express = require("express");
const db = require("../db");

const router = express.Router();

const jsonResponse = (res) => {
    return {
        statusCode: 200,
        header: {
            "Content-Type": "application/json",
        },
        data: res
    }
}

const getAllPosts = async (pool, id) => {
    return db.getAllPosts(pool)
};
  
const getPost = async (pool, id) => {
    return db.getPost(pool,id)
};

const addPost = async (pool, post) => {
    await db.addPost(pool, post)
    return {
        statusCode: 201,
        body: {},
    }
}

router.post("/", async (req, res) => {
    console.log(req)
    pool = await db.createPoolAndValidateSchema();
    const author = req.body.author;
    const content = req.body.content;
    const timestamp = new Date();
  
    try {  
      const post = {
        postedAt: timestamp,
        author: author,
        content: content
      };
      return res.send(await addPost(pool, post))
  
    } catch (err) {
      console.log(err);
    }
  });

router.get("/", async (_req, res) => {
    pool = await db.createPoolAndValidateSchema();
    try {
        return res.json(jsonResponse(await getAllPosts(pool)))
    } catch (err) {
        console.log(err);
    }
});

router.get("/:id/detail", async (req, res) => {
    pool = await db.createPoolAndValidateSchema();
    try {
       return res.json(await getPost(pool, req.params.id));
    } catch (err) {
      console.log(err);
    }
  });
  
module.exports = {
    postsRouter: router,
};