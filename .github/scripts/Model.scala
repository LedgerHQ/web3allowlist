//> using scala "3.3.0"
//> using lib "io.circe::circe-generic:0.14.3"
//> using lib "io.circe::circe-parser:0.14.3"
//> using lib "com.lihaoyi::os-lib:0.9.0"
//> using lib "com.lihaoyi::ammonite-ops:2.4.0"

import ammonite.ops._
import io.circe.jawn._
import io.circe._
import io.circe.syntax._
import io.circe.generic.semiauto._

final case class Contract(address: String)

object Contract {
  implicit val decoder: Decoder[Contract] = deriveDecoder
  implicit val encoder: Encoder[Contract] = deriveEncoder
}

final case class DappAllowList(
    schemaVersion: Int,
    `$schema`: String,
    name: String,
    description: Option[String],
    domain: String,
    subdomains: Option[Seq[String]],
    chains: Map[String, List[Contract]]
)

object DappAllowList {

  implicit val decoder: Decoder[DappAllowList] =
    deriveDecoder
  implicit val encoder: Encoder[DappAllowList] =
    deriveEncoder[DappAllowList].mapJson(_.dropNullValues)
}

final case class DomainAllowList(allowlist: Map[String, List[WebSite]])

object DomainAllowList {

  implicit val decoder: Decoder[DomainAllowList] = deriveDecoder
  implicit val encoder: Encoder[DomainAllowList] =
    deriveEncoder[DomainAllowList].mapJson(_.dropNullValues)
}

final case class WebSite(
    name: String,
    domain: String,
    domains: Option[Seq[String]],
    contracts: List[Contract]
)

object WebSite {
  implicit val decoder: Decoder[WebSite] = deriveDecoder
  implicit val encoder: Encoder[WebSite] =
    deriveEncoder[WebSite].mapJson(_.dropNullValues)
}
