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

val dapps = (ls ! pwd / 'dapps)
  .filter(_.isDir)
  .map(_ / "dapp-allowlist.json")
  .map { path =>
    println(s"Validating ${path}.")
    validate[Model.DappAllowList](path) match {
      case Left(error) =>
        println(s"Error: ${error.getMessage}")
        sys.exit(1)
      case Right(dapp) =>
        dapp
    }
  }

dapps.foreach { dapp =>
  println(s"Validated ${dapp.name}.")
}

val allowlist: Map[String, List[Model.WebSite]] = dapps
  .flatMap(dal =>
    dal.chains.map { case (chain, contracts) =>
      (
        chain,
        Model.WebSite(
          dal.name,
          dal.domain,
          dal.subdomains,
          contracts
        )
      )
    }
  )
  .foldLeft(Map.empty[String, List[Model.WebSite]]) { case (acc, (chain, ws)) =>
    acc.get(chain) match {
      case None    => acc + (chain -> List(ws))
      case Some(l) => acc + (chain -> (ws :: l))
    }
  }

val legacyFile = Model.DomainAllowList(allowlist)

println(legacyFile)

val writer = new java.io.PrintWriter("allowlist-bis.json")
writer.write(legacyFile.asJson.spaces2)
writer.close()

def validate[A](
    path: os.Path
)(implicit dec: Decoder[A]): Either[io.circe.Error, A] = {
  val chan =
    Channels.newChannel(path.getInputStream)
  decodeChannel[A](chan)
}
