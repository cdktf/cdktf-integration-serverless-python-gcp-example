const Knex = require("knex");

const createTcpPool = async (config) => {

  const dbSocketAddr = process.env.DB_HOST.split(":"); 

  // Create connection to the database
  return Knex({
    client: "pg",
    connection: {
      user: process.env.DB_USER, 
      password: process.env.DB_PASS, 
      database: process.env.DB_NAME, 
      host: dbSocketAddr[0], 
      port: dbSocketAddr[1], 
    },
    ...config,
  });
};

const createPool = async () => {
  const config = { pool: {} };
  config.pool.max = 5;
  config.pool.min = 5;
  config.pool.acquireTimeoutMillis = 60000;
  config.pool.idleTimeoutMillis = 600000;
  config.pool.createRetryIntervalMillis = 200;
  return createTcpPool(config);
};

const validateSchema = async (pool) => {
  const hasTable = await pool.schema.hasTable("posts");
  if (!hasTable) {
    return pool.schema.createTable("posts", (table) => {
      table.increments("id").primary();
      table.timestamp("postedAt", 30).notNullable();
      table.specificType("author", "VARCHAR(100)").notNullable();
      table.specificType("content", "VARCHAR(200)").notNullable();
    });
  }
};

const createPoolAndValidateSchema = async () =>
  await createPool()
    .then(async (pool) => {
      await validateSchema(pool);
      return pool;
    })
    .catch((err) => {
      console.log(err);
      throw err;
    });

const getAllPosts = async (pool) => {
    return await pool
        .select("id", "postedAt", "author", "content")
        .from("posts")
        .orderBy("postedAt", "desc");
};
    
const getPost = async (pool, id) => {
    result = await pool("posts").where({ id: id })
    if(result.length === 0){
      return [];
    } else {
      return result[0];
    }
};

const addPost = async (pool, post) => {
    try {
        return await pool("posts").insert(post);
    } catch (err) {
        throw Error(err);
    }
}


module.exports = {
    createPoolAndValidateSchema,
    getAllPosts,
    getPost,
    addPost
};