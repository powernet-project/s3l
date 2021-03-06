<?php

/**
 * API for MediaWiki 1.14+
 *
 * Created on Sep 2, 2008
 *
 * Copyright © 2008 Chad Horohoe
 *
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License along
 * with this program; if not, write to the Free Software Foundation, Inc.,
 * 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
 * http://www.gnu.org/copyleft/gpl.html
 *
 * @file
 */

if ( !defined( 'MEDIAWIKI' ) ) {
	require_once( 'ApiBase.php' );
}

/**
 * API interface for page purging
 * @ingroup API
 */
class ApiPurge extends ApiBase {

	public function __construct( $main, $action ) {
		parent::__construct( $main, $action );
	}

	/**
	 * Purges the cache of a page
	 */
	public function execute() {
		global $wgUser;
		$params = $this->extractRequestParams();
		if ( !$wgUser->isAllowed( 'purge' ) && !$this->getMain()->isInternalMode() &&
				!$this->getMain()->getRequest()->wasPosted() ) {
			$this->dieUsageMsg( array( 'mustbeposted', $this->getModuleName() ) );
		}

		$forceLinkUpdate = $params['forcelinkupdate'];

		$result = array();
		foreach ( $params['titles'] as $t ) {
			$r = array();
			$title = Title::newFromText( $t );
			if ( !$title instanceof Title ) {
				$r['title'] = $t;
				$r['invalid'] = '';
				$result[] = $r;
				continue;
			}
			ApiQueryBase::addTitleInfo( $r, $title );
			if ( !$title->exists() ) {
				$r['missing'] = '';
				$result[] = $r;
				continue;
			}
			$context = $this->createContext();
			$context->setTitle( $title );
			$article = Article::newFromTitle( $title, $context );
			$article->doPurge(); // Directly purge and skip the UI part of purge().
			$r['purged'] = '';

			if( $forceLinkUpdate ) {
				if ( !$wgUser->pingLimiter() ) {
					global $wgParser, $wgEnableParserCache;
					$popts = new ParserOptions();
					$p_result = $wgParser->parse( $article->getContent(), $title, $popts );

					# Update the links tables
					$u = new LinksUpdate( $title, $p_result );
					$u->doUpdate();

					$r['linkupdate'] = '';

					if ( $wgEnableParserCache ) {
						$pcache = ParserCache::singleton();
						$pcache->save( $p_result, $article, $popts );
					}
				} else {
					$this->setWarning( $this->parseMsg( array( 'actionthrottledtext' ) ) );
					$forceLinkUpdate = false;
				}
			}

			$result[] = $r;
		}
		$apiResult = $this->getResult();
		$apiResult->setIndexedTagName( $result, 'page' );
		$apiResult->addValue( null, $this->getModuleName(), $result );
	}

	public function isWriteMode() {
		return true;
	}

	public function getAllowedParams() {
		return array(
			'titles' => array(
				ApiBase::PARAM_ISMULTI => true,
				ApiBase::PARAM_REQUIRED => true
			),
			'forcelinkupdate' => false,
		);
	}

	public function getParamDescription() {
		return array(
			'titles' => 'A list of titles',
			'forcelinkupdate' => 'Update the links tables',
		);
	}

	public function getDescription() {
		return array( 'Purge the cache for the given titles.',
			'Requires a POST request if the user is not logged in.'
		);
	}

	public function getPossibleErrors() {
		return array_merge( parent::getPossibleErrors(), array(
			array( 'cantpurge' ),
		) );
	}

	protected function getExamples() {
		return array(
			'api.php?action=purge&titles=Main_Page|API'
		);
	}

	public function getHelpUrls() {
		return 'https://www.mediawiki.org/wiki/API:Purge';
	}

	public function getVersion() {
		return __CLASS__ . ': $Id: ApiPurge.php 104449 2011-11-28 15:52:04Z reedy $';
	}
}
