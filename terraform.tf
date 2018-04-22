# export HEROKU_EMAIL="ops@company.com"
# export HEROKU_API_KEY="heroku_api_key"

# variable "heroku_email" {}
# variable "heroku_api_key" {}
variable "heroku_app_name" { default = "rkn-vpn-configurator" }

provider "heroku" {
#   email   = "${var.heroku_email}"
#   api_key = "${var.heroku_api_key}"
}

resource "heroku_app" "default" {
  name = "${var.heroku_app_name}"
  region = "eu"
}

# resource "heroku_addon" "postgresql" {
#   app  = "${heroku_app.default.name}"
#   plan = "heroku-postgresql:hobby-dev"
# }

resource "heroku_build" "default" {
  app        = "${heroku_app.default.id}"
  source = {
    path = "."
  }
  depends_on = ["heroku_app.default"]
}

resource "heroku_formation" "default" {
  app        = "${heroku_app.default.id}"
  type       = "web"
  quantity   = 1
  size       = "free"
  depends_on = ["heroku_build.default"]
}

output "url" { value = "https://${heroku_app.default.name}.herokuapp.com/" }
