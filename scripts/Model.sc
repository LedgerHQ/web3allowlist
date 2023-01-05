import $ivy.`io.circe::circe-generic:0.14.3`
import $ivy.`io.circe::circe-parser:0.14.3`
import $ivy.`com.lihaoyi::os-lib:0.9.0`
import $ivy.`com.lihaoyi::ammonite-ops:2.4.0`

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
    name: String,
    domain: String,
    description: Option[String],
    subdomains: Option[List[String]],
    chains: Map[String, List[Contract]]
)

object DappAllowList {

  implicit val decoder: Decoder[DappAllowList] = deriveDecoder
}

final case class DomainAllowList(allowlist: Map[String, List[WebSite]])

object DomainAllowList {

  implicit val decoder: Decoder[DomainAllowList] = deriveDecoder
  implicit val encoder: Encoder[DomainAllowList] = deriveEncoder
}

final case class WebSite(
    name: String,
    domain: String,
    domains: Option[Seq[String]],
    contracts: List[Contract]
)

object WebSite {
  implicit val decoder: Decoder[WebSite] = deriveDecoder
  implicit val encoder: Encoder[WebSite] = deriveEncoder
}
