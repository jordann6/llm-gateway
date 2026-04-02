output "log_archive_bucket_name" {
  value = aws_s3_bucket.log_archive.id
}

output "log_archive_bucket_arn" {
  value = aws_s3_bucket.log_archive.arn
}

output "s3_kms_key_arn" {
  value = aws_kms_key.s3.arn
}