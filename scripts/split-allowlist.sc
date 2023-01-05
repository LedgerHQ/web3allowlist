import $ivy.`io.circe::circe-generic:0.14.3`
import $ivy.`io.circe::circe-parser:0.14.3`
import $ivy.`com.lihaoyi::os-lib:0.9.0`
import $ivy.`com.lihaoyi::ammonite-ops:2.4.0`

import ammonite.ops._
import io.circe.jawn._
import io.circe._
import io.circe.syntax._
import io.circe.generic.semiauto._

import java.nio.channels.Channels

import $file.Model

val allowList = parseLegacy[Model.DomainAllowList](pwd / "allowlist.json")
(allowList match {
  case Left(error) =>
    println(s"Error: ${error.getMessage}")
    sys.exit(1)
  case Right(allowList) =>
    println(allowList)
    allowList.allowlist.flatMap {
      case (chain, sites) if chain == "ethereum" =>
        println(s"Chain: ${chain}")
        sites.map { site =>
          println(s"  Site: ${site.name}")
          println(s"    Domain: ${site.domain}")
          Model.DappAllowList(
            site.name,
            None,
            site.domain,
            site.domains,
            Map(
              chain -> site.contracts.map(c => c.copy(address = c.address.trim))
            )
          )
        }
      case _ => Nil
    }
}).foreach { dapp =>
  val domain =
    if (dapp.domain.startsWith("*.")) dapp.domain.drop(2) else dapp.domain
  mkdir ! pwd / 'dapps / domain
  val writer = new java.io.PrintWriter(
    (pwd / 'dapps / domain / "dapp-allowlist.json").toString
  )
  writer.write(dapp.asJson.spaces2)
  writer.close()

}

def parseLegacy[A](
    path: os.Path
)(implicit dec: Decoder[A]): Either[io.circe.Error, A] = {
  val chan =
    Channels.newChannel(path.getInputStream)
  decodeChannel[A](chan)
}
