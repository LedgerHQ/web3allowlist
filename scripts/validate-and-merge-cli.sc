// Description: Validate and merge the CLI
//> using scala "3.2.1"
//> using repository "https://NOBODY:{{ GITHUB_TOKEN }}@maven.pkg.github.com/LedgerHQ/_"
//> using lib "io.circe::circe-generic:0.14.3"
//> using lib "io.circe::circe-parser:0.14.3"
//> using lib "com.lihaoyi::os-lib:0.9.0"
//> using lib "co.ledger::backend-commons-circe:1.7.1"

import os.*
import language.deprecated.symbolLiterals
import io.circe.jawn.*
import io.circe.*
import io.circe.syntax.*
import io.circe.generic.semiauto.*
import co.ledger.circe.CustomDecodingFailure
import java.nio.channels.Channels
import scala.util.Try
import scala.util.Failure
import scala.util.Success
import scala.util.Using

@main
def main(output: String): Unit = {

  val dapps = list(pwd / 'dapps)
    .filter(os.isDir)
    .map(_ / "dapp-allowlist.json")
    .map { path =>
      println(s"Validating ${path}.")
      validate[DappAllowList](path) match {
        case Failure(error) =>
          sys.error(s"Could not validate file: ${path}")
        case Success(Left(error)) =>
          val errorMessage = error match {
            case decodingFailure: DecodingFailure =>
              s"Error: ${CustomDecodingFailure.showDecodingFailure.show(decodingFailure)}"
            case _ =>
              s"Error: ${error}"
          }
          Console.err.println(s"Invalid file ${path} - ${errorMessage}")
          sys.exit(1)
        case Success(Right(dapp)) => dapp
      }
    }

  val allowlist: Map[String, List[WebSite]] = dapps
    .flatMap(dal =>
      dal.chains.map { case (chain, contracts) =>
        (
          chain,
          WebSite(
            dal.name,
            dal.domain,
            dal.subdomains,
            contracts
          )
        )
      }
    )
    .foldLeft(Map.empty[String, List[WebSite]]) { case (acc, (chain, ws)) =>
      acc.get(chain) match {
        case None    => acc + (chain -> List(ws))
        case Some(l) => acc + (chain -> (ws :: l))
      }
    }

  val legacyFile = DomainAllowList(allowlist)

  Using(new java.io.PrintWriter(output)) { writer =>
    writer.write(legacyFile.asJson.spaces2)
  }
}
def validate[A](
    path: os.Path
)(implicit dec: Decoder[A]): Try[Either[io.circe.Error, A]] = {
  Using(Channels.newChannel(path.getInputStream)) { chan =>
    decodeChannel[A](chan)
  }

}

final case class Contract(address: String)

object Contract {
  implicit val decoder: Decoder[Contract] = deriveDecoder
  implicit val encoder: Encoder[Contract] = deriveEncoder
}

final case class DappAllowList(
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
