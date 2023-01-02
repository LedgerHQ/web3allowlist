import $ivy.`io.circe::circe-generic:0.14.3`
import $ivy.`io.circe::circe-parser:0.14.3`
import $ivy.`com.lihaoyi::os-lib:0.9.0`
import os._
import io.circe.jawn._
import io.circe.Decoder
import io.circe.generic.semiauto._

import java.nio.channels.Channels

@main
def main(paths: os.Path*) = {

  paths
    .filter(_.last == "dapp-allowlist.json")
    .foreach { path =>
      println(s"Validating ${path}.")
      validate[DappAllowList](path) match {
        case Left(error) =>
          println(s"Error: ${error.getMessage}")
          sys.exit(1)
        case Right(_) =>
      }
    }
}

def validate[A](
    path: os.Path
)(implicit dec: Decoder[A]): Either[io.circe.Error, A] = {
  val chan =
    Channels.newChannel(path.getInputStream)
  decodeChannel[A](chan)
}

final case class Contract(address: String)

object Contract {
  implicit val decoder: Decoder[Contract] = deriveDecoder
}

final case class DappAllowList(
    name: String,
    domain: String,
    description: Option[String],
    allowAllSubdomains: Boolean,
    subdomains: Option[List[String]],
    chains: Map[String, List[Contract]]
)

object DappAllowList {

  implicit val decoder: Decoder[DappAllowList] = deriveDecoder
}
