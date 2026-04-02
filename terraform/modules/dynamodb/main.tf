# Request log table (write heavy, TTL for auto cleanup before Lambda archives)

resource "aws_dynamodb_table" "request_log" {
  name         = "${var.name_prefix}-request-log"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "request_id"
  range_key    = "timestamp"

  attribute {
    name = "request_id"
    type = "S"
  }

  attribute {
    name = "timestamp"
    type = "S"
  }

  attribute {
    name = "client_id"
    type = "S"
  }

  global_secondary_index {
    name            = "client-time-index"
    hash_key        = "client_id"
    range_key       = "timestamp"
    projection_type = "ALL"
  }

  ttl {
    attribute_name = "expires_at"
    enabled        = true
  }

  point_in_time_recovery {
    enabled = false
  }

  tags = merge(var.tags, { Name = "${var.name_prefix}-request-log" })
}

# Prompt cache table (key value lookups by prompt hash)

resource "aws_dynamodb_table" "cache" {
  name         = "${var.name_prefix}-cache"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "prompt_hash"

  attribute {
    name = "prompt_hash"
    type = "S"
  }

  ttl {
    attribute_name = "expires_at"
    enabled        = true
  }

  tags = merge(var.tags, { Name = "${var.name_prefix}-cache" })
}

# Eval table (stores sampled responses and their quality scores)

resource "aws_dynamodb_table" "eval" {
  name         = "${var.name_prefix}-eval"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "eval_id"
  range_key    = "timestamp"

  attribute {
    name = "eval_id"
    type = "S"
  }

  attribute {
    name = "timestamp"
    type = "S"
  }

  attribute {
    name = "provider"
    type = "S"
  }

  global_secondary_index {
    name            = "provider-time-index"
    hash_key        = "provider"
    range_key       = "timestamp"
    projection_type = "ALL"
  }

  ttl {
    attribute_name = "expires_at"
    enabled        = true
  }

  tags = merge(var.tags, { Name = "${var.name_prefix}-eval" })
}