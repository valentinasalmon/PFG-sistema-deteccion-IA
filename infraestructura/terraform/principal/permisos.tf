# Permisos de mínimo privilegio (RNF03 CA4).
# - Rol de la EC2: sus buckets, sus parámetros y Systems Manager.
# - Rol de despliegue: GitHub Actions lo asume con OIDC, sin claves guardadas,
#   solo desde la rama main del repositorio (CP-06).

data "aws_iam_policy_document" "asumir_ec2" {
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["ec2.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "servidor" {
  name               = "${var.proyecto}-servidor"
  assume_role_policy = data.aws_iam_policy_document.asumir_ec2.json
}

resource "aws_iam_role_policy_attachment" "ssm" {
  role       = aws_iam_role.servidor.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore"
}

data "aws_iam_policy_document" "servidor" {
  statement {
    sid       = "ImagenesDeLosCasos"
    actions   = ["s3:GetObject", "s3:PutObject", "s3:DeleteObject", "s3:DeleteObjectVersion"]
    resources = ["${aws_s3_bucket.bucket["imagenes"].arn}/*"]
  }
  statement {
    sid       = "ListarImagenesYVersiones"
    actions   = ["s3:ListBucket", "s3:ListBucketVersions"]
    resources = [aws_s3_bucket.bucket["imagenes"].arn]
  }
  statement {
    sid       = "LeerScriptsYArtefactos"
    actions   = ["s3:GetObject"]
    resources = ["${aws_s3_bucket.bucket["operacion"].arn}/servidor/*", "${aws_s3_bucket.bucket["operacion"].arn}/artefactos/*"]
  }
  statement {
    sid       = "ListarScripts"
    actions   = ["s3:ListBucket"]
    resources = [aws_s3_bucket.bucket["operacion"].arn]
  }
  statement {
    sid       = "GuardarRespaldos"
    actions   = ["s3:PutObject"]
    resources = ["${aws_s3_bucket.bucket["operacion"].arn}/respaldos/*"]
  }
  statement {
    sid       = "LeerConfiguracion"
    actions   = ["ssm:GetParametersByPath", "ssm:GetParameter", "ssm:GetParameters"]
    resources = ["arn:aws:ssm:${var.region}:${data.aws_caller_identity.cuenta.account_id}:parameter${local.prefijo_parametros}*"]
  }
  statement {
    sid       = "DescifrarParametros"
    actions   = ["kms:Decrypt"]
    resources = ["*"]
    condition {
      test     = "StringEquals"
      variable = "kms:ViaService"
      values   = ["ssm.${var.region}.amazonaws.com"]
    }
  }
}

resource "aws_iam_role_policy" "servidor" {
  name   = "plataforma"
  role   = aws_iam_role.servidor.id
  policy = data.aws_iam_policy_document.servidor.json
}

resource "aws_iam_instance_profile" "servidor" {
  name = "${var.proyecto}-servidor"
  role = aws_iam_role.servidor.name
}

# --- Despliegue desde GitHub Actions ---

resource "aws_iam_openid_connect_provider" "github" {
  url            = "https://token.actions.githubusercontent.com"
  client_id_list = ["sts.amazonaws.com"]
}

data "aws_iam_policy_document" "asumir_github" {
  statement {
    actions = ["sts:AssumeRoleWithWebIdentity"]
    principals {
      type        = "Federated"
      identifiers = [aws_iam_openid_connect_provider.github.arn]
    }
    condition {
      test     = "StringEquals"
      variable = "token.actions.githubusercontent.com:aud"
      values   = ["sts.amazonaws.com"]
    }
    condition {
      test     = "StringEquals"
      variable = "token.actions.githubusercontent.com:sub"
      values   = ["repo:${var.repositorio_github}:ref:refs/heads/main"]
    }
  }
}

resource "aws_iam_role" "despliegue" {
  name                 = "${var.proyecto}-despliegue"
  assume_role_policy   = data.aws_iam_policy_document.asumir_github.json
  max_session_duration = 3600
}

data "aws_iam_policy_document" "despliegue" {
  statement {
    sid       = "SubirArtefactos"
    actions   = ["s3:PutObject"]
    resources = ["${aws_s3_bucket.bucket["operacion"].arn}/artefactos/*"]
  }
  statement {
    sid     = "EjecutarDespliegue"
    actions = ["ssm:SendCommand"]
    resources = [
      aws_instance.servidor.arn,
      "arn:aws:ssm:${var.region}::document/AWS-RunShellScript",
    ]
  }
  statement {
    sid       = "SeguirDespliegue"
    actions   = ["ssm:GetCommandInvocation", "ssm:ListCommandInvocations"]
    resources = ["*"]
  }
}

resource "aws_iam_role_policy" "despliegue" {
  name   = "desplegar"
  role   = aws_iam_role.despliegue.id
  policy = data.aws_iam_policy_document.despliegue.json
}
